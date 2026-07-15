import math
from datetime import datetime

from repository.order_repository import OrderRepository
from repository.production_queue_repository import ProductionQueueRepository
from repository.sample_repository import SampleRepository


class ProductionLineController:
    def __init__(
        self,
        order_repository: OrderRepository,
        sample_repository: SampleRepository,
        production_queue_repository: ProductionQueueRepository,
    ):
        self.order_repository = order_repository
        self.sample_repository = sample_repository
        self.production_queue_repository = production_queue_repository

    def advance(self, now: datetime) -> None:
        while True:
            entries = self.production_queue_repository.get_all()
            if not entries:
                return

            head = entries[0]
            sample = self.sample_repository.get_by_id(head.sample_id)

            if head.started_at is None:
                if sample.stock_quantity >= head.quantity:
                    self.sample_repository.decrease_stock(head.sample_id, head.quantity)
                    self.order_repository.update_status(head.order_id, "CONFIRMED")
                    self.production_queue_repository.remove(head.order_id)
                    continue

                shortfall_quantity = head.quantity - sample.stock_quantity
                actual_quantity = math.ceil(shortfall_quantity / sample.yield_rate)
                total_production_minutes = sample.average_production_minutes * actual_quantity
                self.production_queue_repository.update_entry(
                    head.order_id,
                    started_at=now.isoformat(),
                    shortfall_quantity=shortfall_quantity,
                    actual_quantity=actual_quantity,
                    total_production_minutes=total_production_minutes,
                )
                return

            started_at = datetime.fromisoformat(head.started_at)
            elapsed_minutes = (now - started_at).total_seconds() / 60
            if elapsed_minutes < head.total_production_minutes:
                return

            self.sample_repository.increase_stock(head.sample_id, head.actual_quantity)
            self.sample_repository.decrease_stock(head.sample_id, head.quantity)
            self.order_repository.update_status(head.order_id, "CONFIRMED")
            self.production_queue_repository.remove(head.order_id)

    def get_current_status(self, now: datetime):
        self.advance(now)
        entries = self.production_queue_repository.get_all()
        return entries[0] if entries else None

    def get_waiting_queue(self) -> list:
        entries = self.production_queue_repository.get_all()
        return entries[1:]
