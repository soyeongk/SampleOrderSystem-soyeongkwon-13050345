from dataclasses import dataclass, asdict


@dataclass
class Sample:
    sample_id: str
    name: str
    average_production_minutes: float
    yield_rate: float
    stock_quantity: int

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "Sample":
        return Sample(
            sample_id=data["sample_id"],
            name=data["name"],
            average_production_minutes=data["average_production_minutes"],
            yield_rate=data["yield_rate"],
            stock_quantity=data["stock_quantity"],
        )
