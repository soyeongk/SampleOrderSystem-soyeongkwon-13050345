from controllers.approval_controller import ApprovalController
from models.order import Order
from models.sample import Sample
from repository.order_repository import OrderRepository
from repository.production_queue_repository import ProductionQueueRepository
from repository.sample_repository import SampleRepository


class FakeApprovalView:
    def __init__(self, page_commands=None, decision=None):
        self.shown_pages = []
        self._page_commands = list(page_commands or [])
        self._decision = decision
        self.errors = []
        self.results = []
        self.shown_summaries = []

    def show_pending_page(self, page):
        self.shown_pages.append(page)

    def read_page_command(self):
        return self._page_commands.pop(0)

    def show_approval_summary(self, summary):
        self.shown_summaries.append(summary)

    def read_decision(self):
        return self._decision

    def show_error(self, message):
        self.errors.append(message)

    def show_result(self, order_id, new_status):
        self.results.append((order_id, new_status))


def make_controller(
    tmp_path, sample_stock=100, order_quantity=30, order_status="RESERVED", **view_kwargs
):
    sample_repo = SampleRepository(tmp_path / "samples.json")
    sample_repo.create(
        Sample(
            sample_id="S-001",
            name="Wafer-A",
            average_production_minutes=30.0,
            yield_rate=0.9,
            stock_quantity=sample_stock,
        )
    )
    order_repo = OrderRepository(tmp_path / "orders.json")
    order_repo.create(
        Order(
            order_id="ORD-1",
            sample_id="S-001",
            customer_name="ACME Corp",
            quantity=order_quantity,
            status=order_status,
        )
    )
    queue_repo = ProductionQueueRepository(tmp_path / "production_queue.json")
    view = FakeApprovalView(**view_kwargs)
    controller = ApprovalController(order_repo, sample_repo, queue_repo, view)
    return controller, order_repo, sample_repo, queue_repo, view


def test_list_pending_orders_returns_only_reserved(tmp_path):
    controller, order_repo, _, _, view = make_controller(tmp_path, order_status="RESERVED")
    order_repo.create(
        Order(
            order_id="ORD-2",
            sample_id="S-001",
            customer_name="Other Corp",
            quantity=5,
            status="CONFIRMED",
        )
    )

    pending = controller.list_pending_orders()

    assert [o.order_id for o in pending] == ["ORD-1"]


def test_approve_confirms_order_when_stock_sufficient(tmp_path):
    controller, order_repo, sample_repo, queue_repo, _ = make_controller(
        tmp_path, sample_stock=100, order_quantity=30
    )

    controller.approve("ORD-1")

    assert order_repo.get_all()[0].status == "CONFIRMED"
    assert sample_repo.get_by_id("S-001").stock_quantity == 70
    assert queue_repo.get_all() == []


def test_approve_enqueues_production_when_stock_insufficient(tmp_path):
    controller, order_repo, sample_repo, queue_repo, _ = make_controller(
        tmp_path, sample_stock=5, order_quantity=20
    )

    controller.approve("ORD-1")

    assert order_repo.get_all()[0].status == "PRODUCING"
    assert sample_repo.get_by_id("S-001").stock_quantity == 5
    queued = queue_repo.get_all()
    assert len(queued) == 1
    assert queued[0].order_id == "ORD-1"
    assert queued[0].sample_id == "S-001"
    assert queued[0].quantity == 20
    assert queued[0].started_at is None


def test_reject_sets_rejected_status_without_touching_stock(tmp_path):
    controller, order_repo, sample_repo, queue_repo, _ = make_controller(
        tmp_path, sample_stock=100, order_quantity=30
    )

    controller.reject("ORD-1")

    assert order_repo.get_all()[0].status == "REJECTED"
    assert sample_repo.get_by_id("S-001").stock_quantity == 100
    assert queue_repo.get_all() == []


def test_build_approval_summary_when_stock_sufficient(tmp_path):
    controller, order_repo, _, _, _ = make_controller(
        tmp_path, sample_stock=100, order_quantity=30
    )
    order = order_repo.get_all()[0]

    summary = controller.build_approval_summary(order)

    assert summary.sample_name == "Wafer-A"
    assert summary.current_stock == 100
    assert summary.order_quantity == 30
    assert summary.shortfall == 0
    assert summary.is_insufficient is False
    assert summary.actual_quantity is None
    assert summary.total_production_minutes is None


def test_build_approval_summary_when_stock_insufficient(tmp_path):
    controller, order_repo, _, _, _ = make_controller(
        tmp_path, sample_stock=5, order_quantity=20
    )
    order = order_repo.get_all()[0]

    summary = controller.build_approval_summary(order)

    assert summary.shortfall == 15
    assert summary.is_insufficient is True
    assert summary.actual_quantity == 17  # ceil(15 / 0.9)
    assert summary.total_production_minutes == 30.0 * 17


def test_handle_menu_shows_summary_before_decision(tmp_path):
    controller, order_repo, _, _, view = make_controller(
        tmp_path, page_commands=["1"], decision="1"
    )

    controller.handle_menu()

    assert len(view.shown_summaries) == 1
    assert view.shown_summaries[0].sample_name == "Wafer-A"


def test_handle_menu_approves_selected_order_when_decision_is_1(tmp_path):
    controller, order_repo, _, _, view = make_controller(
        tmp_path, page_commands=["1"], decision="1"
    )

    controller.handle_menu()

    assert order_repo.get_all()[0].status == "CONFIRMED"
    assert view.results == [("ORD-1", "CONFIRMED")]


def test_handle_menu_rejects_selected_order_when_decision_is_2(tmp_path):
    controller, order_repo, _, _, view = make_controller(
        tmp_path, page_commands=["1"], decision="2"
    )

    controller.handle_menu()

    assert order_repo.get_all()[0].status == "REJECTED"
    assert view.results == [("ORD-1", "REJECTED")]


def test_handle_menu_shows_error_for_out_of_range_selection(tmp_path):
    controller, order_repo, _, _, view = make_controller(
        tmp_path, page_commands=["9"], decision="1"
    )

    controller.handle_menu()

    assert order_repo.get_all()[0].status == "RESERVED"
    assert len(view.errors) == 1


def test_handle_menu_shows_error_for_invalid_decision(tmp_path):
    controller, order_repo, _, _, view = make_controller(
        tmp_path, page_commands=["1"], decision="9"
    )

    controller.handle_menu()

    assert order_repo.get_all()[0].status == "RESERVED"
    assert len(view.errors) == 1


def test_handle_menu_returns_to_menu_when_back_command_given(tmp_path):
    controller, order_repo, sample_repo, queue_repo, view = make_controller(
        tmp_path, page_commands=["b"]
    )

    controller.handle_menu()

    assert order_repo.get_all()[0].status == "RESERVED"
    assert sample_repo.get_by_id("S-001").stock_quantity == 100
    assert queue_repo.get_all() == []
    assert view.errors == []
    assert view.results == []


def test_handle_menu_navigates_to_next_page_before_selecting(tmp_path):
    controller, order_repo, sample_repo, queue_repo, view = make_controller(
        tmp_path, page_commands=["n", "1"], decision="1"
    )
    for i in range(2, 13):
        order_repo.create(
            Order(
                order_id=f"ORD-{i}",
                sample_id="S-001",
                customer_name="Other Corp",
                quantity=1,
                status="RESERVED",
            )
        )

    controller.handle_menu()

    assert len(view.shown_pages) == 2
    statuses = {o.order_id: o.status for o in order_repo.get_all()}
    assert statuses["ORD-11"] == "CONFIRMED"
