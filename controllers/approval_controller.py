import math
from dataclasses import dataclass

from controllers.pagination import paginate, resolve_page_selection
from models.order import Order
from models.production_queue_entry import ProductionQueueEntry
from repository.order_repository import OrderRepository
from repository.production_queue_repository import ProductionQueueRepository
from repository.sample_repository import SampleRepository


@dataclass
class ApprovalSummary:
    sample_name: str
    current_stock: int
    order_quantity: int
    shortfall: int
    is_insufficient: bool
    actual_quantity: int | None
    total_production_minutes: float | None


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
            self.production_queue_repository.enqueue(
                ProductionQueueEntry(
                    order_id=order_id,
                    sample_id=sample.sample_id,
                    quantity=order.quantity,
                )
            )
            self.order_repository.update_status(order_id, "PRODUCING")

    def reject(self, order_id: str) -> None:
        self.order_repository.update_status(order_id, "REJECTED")

    def build_approval_summary(self, order: Order) -> ApprovalSummary:
        sample = self.sample_repository.get_by_id(order.sample_id)
        is_insufficient = sample.stock_quantity < order.quantity
        shortfall = max(0, order.quantity - sample.stock_quantity)

        actual_quantity = None
        total_production_minutes = None
        if is_insufficient:
            actual_quantity = math.ceil(shortfall / sample.yield_rate)
            total_production_minutes = sample.average_production_minutes * actual_quantity

        return ApprovalSummary(
            sample_name=sample.name,
            current_stock=sample.stock_quantity,
            order_quantity=order.quantity,
            shortfall=shortfall,
            is_insufficient=is_insufficient,
            actual_quantity=actual_quantity,
            total_production_minutes=total_production_minutes,
        )

    def handle_menu(self) -> None:
        pending_orders = self.list_pending_orders()
        if not pending_orders:
            self.approval_view.show_pending_page(paginate([], 1))
            return

        selected_order = None
        page_number = 1
        while selected_order is None:
            page = paginate(pending_orders, page_number)
            self.approval_view.show_pending_page(page)
            command = self.approval_view.read_page_command()

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
                self.approval_view.show_error("올바른 선택이 아닙니다.")
                return

        order_id = selected_order.order_id
        self.approval_view.show_approval_summary(self.build_approval_summary(selected_order))
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
