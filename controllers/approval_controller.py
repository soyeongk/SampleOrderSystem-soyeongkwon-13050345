from models.order import Order
from models.production_queue_entry import ProductionQueueEntry
from repository.order_repository import OrderRepository
from repository.production_queue_repository import ProductionQueueRepository
from repository.sample_repository import SampleRepository


class ApprovalController:
    def __init__(
        self,
        order_repository: OrderRepository,
        sample_repository: SampleRepository,
        production_queue_repository: ProductionQueueRepository,
        approval_view,
    ):
        self.order_repository = order_repository
        self.sample_repository = sample_repository
        self.production_queue_repository = production_queue_repository
        self.approval_view = approval_view

    def list_pending_orders(self) -> list[Order]:
        return [o for o in self.order_repository.get_all() if o.status == "RESERVED"]

    def approve(self, order_id: str) -> None:
        order = next(o for o in self.order_repository.get_all() if o.order_id == order_id)
        sample = self.sample_repository.get_by_id(order.sample_id)

        if sample.stock_quantity >= order.quantity:
            self.sample_repository.decrease_stock(sample.sample_id, order.quantity)
            self.order_repository.update_status(order_id, "CONFIRMED")
        else:
            shortfall_quantity = order.quantity - sample.stock_quantity
            self.sample_repository.decrease_stock(sample.sample_id, sample.stock_quantity)
            self.production_queue_repository.enqueue(
                ProductionQueueEntry(
                    order_id=order_id,
                    sample_id=sample.sample_id,
                    shortfall_quantity=shortfall_quantity,
                )
            )
            self.order_repository.update_status(order_id, "PRODUCING")

    def reject(self, order_id: str) -> None:
        self.order_repository.update_status(order_id, "REJECTED")

    def handle_menu(self) -> None:
        pending_orders = self.list_pending_orders()
        self.approval_view.show_pending_orders(pending_orders)
        if not pending_orders:
            return

        order_id = self.approval_view.read_target_order_id()
        if order_id not in {o.order_id for o in pending_orders}:
            self.approval_view.show_error("승인 대기 중인 주문번호가 아닙니다.")
            return

        decision = self.approval_view.read_decision()
        if decision == "1":
            self.approve(order_id)
            new_status = next(
                o.status for o in self.order_repository.get_all() if o.order_id == order_id
            )
            self.approval_view.show_result(order_id, new_status)
        elif decision == "2":
            self.reject(order_id)
            self.approval_view.show_result(order_id, "REJECTED")
        else:
            self.approval_view.show_error("올바른 선택이 아닙니다.")
