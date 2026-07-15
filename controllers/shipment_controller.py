from controllers.pagination import paginate, resolve_page_selection
from models.order import Order
from repository.order_repository import OrderRepository


class ShipmentController:
    def __init__(self, order_repository: OrderRepository, shipment_view):
        self.order_repository = order_repository
        self.shipment_view = shipment_view

    def list_shippable_orders(self) -> list[Order]:
        return [o for o in self.order_repository.get_all() if o.status == "CONFIRMED"]

    def ship(self, order_id: str) -> None:
        self.order_repository.update_status(order_id, "RELEASED")

    def handle_menu(self) -> None:
        shippable_orders = self.list_shippable_orders()
        if not shippable_orders:
            self.shipment_view.show_shippable_page(paginate([], 1))
            return

        selected_order = None
        page_number = 1
        while selected_order is None:
            page = paginate(shippable_orders, page_number)
            self.shipment_view.show_shippable_page(page)
            command = self.shipment_view.read_page_command()

            if command == "n":
                page_number += 1
                continue
            if command == "p":
                page_number -= 1
                continue
            if command == "b":
                return

            selected_order = resolve_page_selection(page, command)
            if selected_order is None:
                self.shipment_view.show_error("올바른 선택이 아닙니다.")
                return

        self.ship(selected_order.order_id)
        self.shipment_view.show_result(selected_order.order_id, "RELEASED")
