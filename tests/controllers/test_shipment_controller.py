from controllers.shipment_controller import ShipmentController
from models.order import Order
from repository.order_repository import OrderRepository


class FakeShipmentView:
    def __init__(self, target_order_id=None):
        self.shown_lists = []
        self._target_order_id = target_order_id
        self.errors = []
        self.results = []

    def show_shippable_orders(self, orders):
        self.shown_lists.append(orders)

    def read_target_order_id(self):
        return self._target_order_id

    def show_error(self, message):
        self.errors.append(message)

    def show_result(self, order_id, new_status):
        self.results.append((order_id, new_status))


def make_controller(tmp_path, order_status="CONFIRMED", **view_kwargs):
    order_repo = OrderRepository(tmp_path / "orders.json")
    order_repo.create(
        Order(
            order_id="ORD-1",
            sample_id="S-001",
            customer_name="ACME Corp",
            quantity=10,
            status=order_status,
        )
    )
    view = FakeShipmentView(**view_kwargs)
    controller = ShipmentController(order_repo, view)
    return controller, order_repo, view


def test_list_shippable_orders_returns_only_confirmed(tmp_path):
    controller, order_repo, _ = make_controller(tmp_path, order_status="CONFIRMED")
    order_repo.create(
        Order(
            order_id="ORD-2",
            sample_id="S-001",
            customer_name="Other Corp",
            quantity=5,
            status="RESERVED",
        )
    )

    shippable = controller.list_shippable_orders()

    assert [o.order_id for o in shippable] == ["ORD-1"]


def test_ship_changes_status_to_released(tmp_path):
    controller, order_repo, _ = make_controller(tmp_path, order_status="CONFIRMED")

    controller.ship("ORD-1")

    assert order_repo.get_all()[0].status == "RELEASED"


def test_handle_menu_ships_selected_order(tmp_path):
    controller, order_repo, view = make_controller(
        tmp_path, order_status="CONFIRMED", target_order_id="ORD-1"
    )

    controller.handle_menu()

    assert order_repo.get_all()[0].status == "RELEASED"
    assert view.results == [("ORD-1", "RELEASED")]


def test_handle_menu_shows_error_for_unknown_order_id(tmp_path):
    controller, order_repo, view = make_controller(
        tmp_path, order_status="CONFIRMED", target_order_id="ORD-999"
    )

    controller.handle_menu()

    assert order_repo.get_all()[0].status == "CONFIRMED"
    assert len(view.errors) == 1


def test_handle_menu_does_nothing_when_no_shippable_orders(tmp_path):
    controller, order_repo, view = make_controller(
        tmp_path, order_status="RESERVED", target_order_id="ORD-1"
    )

    controller.handle_menu()

    assert order_repo.get_all()[0].status == "RESERVED"
    assert view.errors == []
    assert view.results == []
