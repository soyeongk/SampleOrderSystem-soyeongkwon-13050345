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
        self.shipment_view.show_shippable_orders(shippable_orders)
        if not shippable_orders:
            return

        order_id = self.shipment_view.read_target_order_id()
        if order_id not in {o.order_id for o in shippable_orders}:
            self.shipment_view.show_error("출고 가능한 주문번호가 아닙니다.")
            return

        self.ship(order_id)
        self.shipment_view.show_result(order_id, "RELEASED")
