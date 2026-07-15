from dataclasses import dataclass, asdict


@dataclass
class Order:
    order_id: str
    sample_id: str
    customer_name: str
    quantity: int
    status: str

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "Order":
        return Order(
            order_id=data["order_id"],
            sample_id=data["sample_id"],
            customer_name=data["customer_name"],
            quantity=data["quantity"],
            status=data["status"],
        )
