from controllers.order_controller import OrderController
from models.sample import Sample
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository


class FakeOrderView:
    def __init__(self, new_order_input=None):
        self._new_order_input = new_order_input
        self.order_successes = []
        self.order_errors = []

    def show_order_menu(self):
        pass

    def read_new_order_input(self):
        return self._new_order_input

    def show_order_success(self, order):
        self.order_successes.append(order)

    def show_order_error(self, message):
        self.order_errors.append(message)


def make_controller(tmp_path, registered_sample=True, **view_kwargs):
    sample_repo = SampleRepository(tmp_path / "samples.json")
    if registered_sample:
        sample_repo.create(
            Sample(
                sample_id="S-001",
                name="Wafer-A",
                average_production_minutes=30.0,
                yield_rate=0.9,
                stock_quantity=100,
            )
        )
    order_repo = OrderRepository(tmp_path / "orders.json")
    view = FakeOrderView(**view_kwargs)
    return OrderController(order_repo, sample_repo, view), order_repo, view


def test_reserve_order_creates_order_with_reserved_status(tmp_path):
    controller, order_repo, view = make_controller(
        tmp_path,
        new_order_input={
            "sample_id": "S-001",
            "customer_name": "ACME Corp",
            "quantity": "10",
        },
    )

    controller.reserve_order()

    all_orders = order_repo.get_all()
    assert len(all_orders) == 1
    assert all_orders[0].status == "RESERVED"
    assert all_orders[0].sample_id == "S-001"
    assert view.order_successes[0].status == "RESERVED"


def test_reserve_order_does_not_check_or_decrease_stock(tmp_path):
    controller, order_repo, view = make_controller(
        tmp_path,
        new_order_input={
            "sample_id": "S-001",
            "customer_name": "ACME Corp",
            "quantity": "9999",
        },
    )

    controller.reserve_order()

    assert order_repo.get_all()[0].status == "RESERVED"


def test_reserve_order_rejects_nonexistent_sample_id(tmp_path):
    controller, order_repo, view = make_controller(
        tmp_path,
        registered_sample=False,
        new_order_input={
            "sample_id": "S-999",
            "customer_name": "ACME Corp",
            "quantity": "10",
        },
    )

    controller.reserve_order()

    assert order_repo.get_all() == []
    assert len(view.order_errors) == 1


def test_reserve_order_rejects_empty_customer_name(tmp_path):
    controller, order_repo, view = make_controller(
        tmp_path,
        new_order_input={
            "sample_id": "S-001",
            "customer_name": "",
            "quantity": "10",
        },
    )

    controller.reserve_order()

    assert order_repo.get_all() == []
    assert len(view.order_errors) == 1


def test_reserve_order_rejects_non_numeric_quantity(tmp_path):
    controller, order_repo, view = make_controller(
        tmp_path,
        new_order_input={
            "sample_id": "S-001",
            "customer_name": "ACME Corp",
            "quantity": "abc",
        },
    )

    controller.reserve_order()

    assert order_repo.get_all() == []
    assert len(view.order_errors) == 1


def test_reserve_order_rejects_non_positive_quantity(tmp_path):
    controller, order_repo, view = make_controller(
        tmp_path,
        new_order_input={
            "sample_id": "S-001",
            "customer_name": "ACME Corp",
            "quantity": "0",
        },
    )

    controller.reserve_order()

    assert order_repo.get_all() == []
    assert len(view.order_errors) == 1
