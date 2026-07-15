from controllers.order_controller import OrderController
from models.sample import Sample
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository


class FakeOrderView:
    def __init__(self, page_commands=None, customer_name=None, quantity=None):
        self._page_commands = list(page_commands or [])
        self._customer_name = customer_name
        self._quantity = quantity
        self.shown_pages = []
        self.order_successes = []
        self.order_errors = []

    def show_sample_page(self, page):
        self.shown_pages.append(page)

    def read_sample_page_command(self):
        return self._page_commands.pop(0)

    def read_customer_name(self):
        return self._customer_name

    def read_quantity(self):
        return self._quantity

    def show_order_success(self, order):
        self.order_successes.append(order)

    def show_order_error(self, message):
        self.order_errors.append(message)


def make_controller(tmp_path, sample_count=1, **view_kwargs):
    sample_repo = SampleRepository(tmp_path / "samples.json")
    for i in range(1, sample_count + 1):
        sample_repo.create(
            Sample(
                sample_id=f"S-{i:03d}",
                name=f"Wafer-{i}",
                average_production_minutes=30.0,
                yield_rate=0.9,
                stock_quantity=100,
            )
        )
    order_repo = OrderRepository(tmp_path / "orders.json")
    view = FakeOrderView(**view_kwargs)
    return OrderController(order_repo, sample_repo, view), order_repo, view


def test_reserve_order_creates_order_for_selected_sample(tmp_path):
    controller, order_repo, view = make_controller(
        tmp_path,
        sample_count=1,
        page_commands=["1"],
        customer_name="ACME Corp",
        quantity="10",
    )

    controller.reserve_order()

    all_orders = order_repo.get_all()
    assert len(all_orders) == 1
    assert all_orders[0].status == "RESERVED"
    assert all_orders[0].sample_id == "S-001"
    assert view.order_successes[0].status == "RESERVED"


def test_reserve_order_navigates_to_next_page_before_selecting(tmp_path):
    controller, order_repo, view = make_controller(
        tmp_path,
        sample_count=12,
        page_commands=["n", "1"],
        customer_name="ACME Corp",
        quantity="10",
    )

    controller.reserve_order()

    all_orders = order_repo.get_all()
    assert all_orders[0].sample_id == "S-011"
    assert len(view.shown_pages) == 2


def test_reserve_order_does_not_check_or_decrease_stock(tmp_path):
    controller, order_repo, view = make_controller(
        tmp_path,
        sample_count=1,
        page_commands=["1"],
        customer_name="ACME Corp",
        quantity="9999",
    )

    controller.reserve_order()

    assert order_repo.get_all()[0].status == "RESERVED"


def test_reserve_order_rejects_out_of_range_selection(tmp_path):
    controller, order_repo, view = make_controller(
        tmp_path,
        sample_count=1,
        page_commands=["9"],
    )

    controller.reserve_order()

    assert order_repo.get_all() == []
    assert len(view.order_errors) == 1


def test_reserve_order_rejects_empty_customer_name(tmp_path):
    controller, order_repo, view = make_controller(
        tmp_path,
        sample_count=1,
        page_commands=["1"],
        customer_name="",
        quantity="10",
    )

    controller.reserve_order()

    assert order_repo.get_all() == []
    assert len(view.order_errors) == 1


def test_reserve_order_rejects_non_numeric_quantity(tmp_path):
    controller, order_repo, view = make_controller(
        tmp_path,
        sample_count=1,
        page_commands=["1"],
        customer_name="ACME Corp",
        quantity="abc",
    )

    controller.reserve_order()

    assert order_repo.get_all() == []
    assert len(view.order_errors) == 1


def test_reserve_order_rejects_non_positive_quantity(tmp_path):
    controller, order_repo, view = make_controller(
        tmp_path,
        sample_count=1,
        page_commands=["1"],
        customer_name="ACME Corp",
        quantity="0",
    )

    controller.reserve_order()

    assert order_repo.get_all() == []
    assert len(view.order_errors) == 1


def test_reserve_order_shows_error_when_no_samples_registered(tmp_path):
    controller, order_repo, view = make_controller(tmp_path, sample_count=0)

    controller.reserve_order()

    assert order_repo.get_all() == []
    assert len(view.order_errors) == 1


def test_reserve_order_returns_to_menu_when_back_command_given(tmp_path):
    controller, order_repo, view = make_controller(
        tmp_path,
        sample_count=1,
        page_commands=["b"],
    )

    controller.reserve_order()

    assert order_repo.get_all() == []
    assert view.order_errors == []
