from controllers.shipment_controller import ShipmentController
from models.order import Order
from repository.order_repository import OrderRepository


class FakeShipmentView:
    def __init__(self, page_commands=None):
        self.shown_pages = []
        self._page_commands = list(page_commands or [])
        self.errors = []
        self.results = []

    def show_shippable_page(self, page):
        self.shown_pages.append(page)

    def read_page_command(self):
        return self._page_commands.pop(0)

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
        tmp_path, order_status="CONFIRMED", page_commands=["1"]
    )

    controller.handle_menu()

    assert order_repo.get_all()[0].status == "RELEASED"
    assert view.results == [("ORD-1", "RELEASED")]


def test_handle_menu_shows_error_for_out_of_range_selection(tmp_path):
    controller, order_repo, view = make_controller(
        tmp_path, order_status="CONFIRMED", page_commands=["9"]
    )

    controller.handle_menu()

    assert order_repo.get_all()[0].status == "CONFIRMED"
    assert len(view.errors) == 1


def test_handle_menu_does_nothing_when_no_shippable_orders(tmp_path):
    controller, order_repo, view = make_controller(
        tmp_path, order_status="RESERVED", page_commands=["1"]
    )

    controller.handle_menu()

    assert order_repo.get_all()[0].status == "RESERVED"
    assert view.errors == []
    assert view.results == []


def test_handle_menu_returns_to_menu_when_back_command_given(tmp_path):
    controller, order_repo, view = make_controller(
        tmp_path, order_status="CONFIRMED", page_commands=["b"]
    )

    controller.handle_menu()

    assert order_repo.get_all()[0].status == "CONFIRMED"
    assert view.errors == []
    assert view.results == []


def test_handle_menu_navigates_to_next_page_before_selecting(tmp_path):
    controller, order_repo, view = make_controller(
        tmp_path, order_status="CONFIRMED", page_commands=["n", "1"]
    )
    for i in range(2, 13):
        order_repo.create(
            Order(
                order_id=f"ORD-{i}",
                sample_id="S-001",
                customer_name="Other Corp",
                quantity=1,
                status="CONFIRMED",
            )
        )

    controller.handle_menu()

    assert len(view.shown_pages) == 2
    statuses = {o.order_id: o.status for o in order_repo.get_all()}
    assert statuses["ORD-11"] == "RELEASED"
