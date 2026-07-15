from controllers.pagination import paginate, resolve_page_selection
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
        samples = self.sample_repository.get_all()
        if not samples:
            self.order_view.show_order_error("등록된 시료가 없습니다.")
            return

        selected_sample = None
        page_number = 1
        while selected_sample is None:
            page = paginate(samples, page_number)
            self.order_view.show_sample_page(page)
            command = self.order_view.read_sample_page_command()

            if command == "n":
                page_number += 1
                continue
            if command == "p":
                page_number -= 1
                continue

            selected_sample = resolve_page_selection(page, command)
            if selected_sample is None:
                self.order_view.show_order_error("올바른 선택이 아닙니다.")
                return

        customer_name = self.order_view.read_customer_name()
        if not customer_name:
            self.order_view.show_order_error("고객명은 비어 있을 수 없습니다.")
            return

        try:
            quantity = int(self.order_view.read_quantity())
        except ValueError:
            self.order_view.show_order_error("주문 수량은 숫자여야 합니다.")
            return

        if quantity <= 0:
            self.order_view.show_order_error("주문 수량은 1 이상이어야 합니다.")
            return

        order = Order(
            order_id=self.order_repository.generate_order_id(),
            sample_id=selected_sample.sample_id,
            customer_name=customer_name,
            quantity=quantity,
            status="RESERVED",
        )
        self.order_repository.create(order)
        self.order_view.show_order_success(order)
