from controllers.approval_controller import ApprovalController
from models.order import Order
from models.sample import Sample
from repository.order_repository import OrderRepository
from repository.production_queue_repository import ProductionQueueRepository
from repository.sample_repository import SampleRepository


class FakeApprovalView:
    def __init__(self, target_order_id=None, decision=None):
        self.shown_lists = []
        self._target_order_id = target_order_id
        self._decision = decision
        self.errors = []
        self.results = []

    def show_pending_orders(self, orders):
        self.shown_lists.append(orders)

    def read_target_order_id(self):
        return self._target_order_id

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
    assert sample_repo.get_by_id("S-001").stock_quantity == 0
    queued = queue_repo.get_all()
    assert len(queued) == 1
    assert queued[0].order_id == "ORD-1"
    assert queued[0].sample_id == "S-001"
    assert queued[0].shortfall_quantity == 15


def test_reject_sets_rejected_status_without_touching_stock(tmp_path):
    controller, order_repo, sample_repo, queue_repo, _ = make_controller(
        tmp_path, sample_stock=100, order_quantity=30
    )

    controller.reject("ORD-1")

    assert order_repo.get_all()[0].status == "REJECTED"
    assert sample_repo.get_by_id("S-001").stock_quantity == 100
    assert queue_repo.get_all() == []


def test_handle_menu_approves_when_decision_is_1(tmp_path):
    controller, order_repo, _, _, view = make_controller(
        tmp_path, target_order_id="ORD-1", decision="1"
    )

    controller.handle_menu()

    assert order_repo.get_all()[0].status == "CONFIRMED"
    assert view.results == [("ORD-1", "CONFIRMED")]


def test_handle_menu_rejects_when_decision_is_2(tmp_path):
    controller, order_repo, _, _, view = make_controller(
        tmp_path, target_order_id="ORD-1", decision="2"
    )

    controller.handle_menu()

    assert order_repo.get_all()[0].status == "REJECTED"
    assert view.results == [("ORD-1", "REJECTED")]


def test_handle_menu_shows_error_for_unknown_order_id(tmp_path):
    controller, order_repo, _, _, view = make_controller(
        tmp_path, target_order_id="ORD-999", decision="1"
    )

    controller.handle_menu()

    assert order_repo.get_all()[0].status == "RESERVED"
    assert len(view.errors) == 1


def test_handle_menu_shows_error_for_invalid_decision(tmp_path):
    controller, order_repo, _, _, view = make_controller(
        tmp_path, target_order_id="ORD-1", decision="9"
    )

    controller.handle_menu()

    assert order_repo.get_all()[0].status == "RESERVED"
    assert len(view.errors) == 1
