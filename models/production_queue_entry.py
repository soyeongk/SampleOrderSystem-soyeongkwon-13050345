from dataclasses import dataclass, asdict


@dataclass
class ProductionQueueEntry:
    order_id: str
    sample_id: str
    quantity: int
    started_at: str | None = None
    shortfall_quantity: int | None = None
    actual_quantity: int | None = None
    total_production_minutes: float | None = None

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "ProductionQueueEntry":
        return ProductionQueueEntry(
            order_id=data["order_id"],
            sample_id=data["sample_id"],
            quantity=data["quantity"],
            started_at=data.get("started_at"),
            shortfall_quantity=data.get("shortfall_quantity"),
            actual_quantity=data.get("actual_quantity"),
            total_production_minutes=data.get("total_production_minutes"),
        )
