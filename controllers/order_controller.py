from models.order import Order
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository


class OrderController:
    def __init__(
        self,
        order_repository: OrderRepository,
        sample_repository: SampleRepository,
        order_view,
    ):
        self.order_repository = order_repository
        self.sample_repository = sample_repository
        self.order_view = order_view

    def reserve_order(self) -> None:
        self.order_view.show_order_menu()
        raw_input_values = self.order_view.read_new_order_input()

        sample = self.sample_repository.get_by_id(raw_input_values["sample_id"])
        if sample is None:
            self.order_view.show_order_error("존재하지 않는 시료 ID입니다.")
            return

        if not raw_input_values["customer_name"]:
            self.order_view.show_order_error("고객명은 비어 있을 수 없습니다.")
            return

        try:
            quantity = int(raw_input_values["quantity"])
        except ValueError:
            self.order_view.show_order_error("주문 수량은 숫자여야 합니다.")
            return

        if quantity <= 0:
            self.order_view.show_order_error("주문 수량은 1 이상이어야 합니다.")
            return

        order = Order(
            order_id=self.order_repository.generate_order_id(),
            sample_id=sample.sample_id,
            customer_name=raw_input_values["customer_name"],
            quantity=quantity,
            status="RESERVED",
        )
        self.order_repository.create(order)
        self.order_view.show_order_success(order)
