from datetime import datetime

from models.order import Order
from repository.json_repository import load_json, save_json


class OrderRepository:
    def __init__(self, file_path):
        self.file_path = file_path

    def get_all(self) -> list[Order]:
        return [Order.from_dict(item) for item in load_json(self.file_path)]

    def create(self, order: Order) -> Order:
        orders = self.get_all()
        if any(o.order_id == order.order_id for o in orders):
            raise ValueError(f"이미 존재하는 주문번호입니다: {order.order_id}")
        orders.append(order)
        save_json(self.file_path, [o.to_dict() for o in orders])
        return order

    def generate_order_id(self, base_time: datetime | None = None) -> str:
        base_time = base_time or datetime.now()
        prefix = f"ORD-{base_time.strftime('%Y%m%d-%H%M')}"
        existing_ids = {order.order_id for order in self.get_all()}
        seq = 1
        while True:
            candidate = f"{prefix}-{seq:02d}"
            if candidate not in existing_ids:
                return candidate
            seq += 1
