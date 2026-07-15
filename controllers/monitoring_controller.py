from dataclasses import dataclass

from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository

MONITORED_STATUSES = ("RESERVED", "CONFIRMED", "PRODUCING", "RELEASED")
PENDING_STATUSES = ("RESERVED", "PRODUCING")


@dataclass
class InventoryStatusRow:
    sample_id: str
    name: str
    stock_quantity: int
    pending_demand: int
    status: str


class MonitoringController:
    def __init__(self, order_repository: OrderRepository, sample_repository: SampleRepository):
        self.order_repository = order_repository
        self.sample_repository = sample_repository

    def get_order_status_counts(self) -> dict:
        counts = {status: 0 for status in MONITORED_STATUSES}
        for order in self.order_repository.get_all():
            if order.status in counts:
                counts[order.status] += 1
        return counts

    def get_inventory_status(self) -> list[InventoryStatusRow]:
        orders = self.order_repository.get_all()
        pending_by_sample = {}
        for order in orders:
            if order.status in PENDING_STATUSES:
                pending_by_sample[order.sample_id] = (
                    pending_by_sample.get(order.sample_id, 0) + order.quantity
                )

        rows = []
        for sample in self.sample_repository.get_all():
            pending_demand = pending_by_sample.get(sample.sample_id, 0)
            if sample.stock_quantity <= 0:
                status = "고갈"
            elif sample.stock_quantity < pending_demand:
                status = "부족"
            else:
                status = "여유"
            rows.append(
                InventoryStatusRow(
                    sample_id=sample.sample_id,
                    name=sample.name,
                    stock_quantity=sample.stock_quantity,
                    pending_demand=pending_demand,
                    status=status,
                )
            )
        return rows
