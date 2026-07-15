from dataclasses import dataclass, asdict


@dataclass
class ProductionQueueEntry:
    order_id: str
    sample_id: str
    shortfall_quantity: int

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "ProductionQueueEntry":
        return ProductionQueueEntry(
            order_id=data["order_id"],
            sample_id=data["sample_id"],
            shortfall_quantity=data["shortfall_quantity"],
        )
