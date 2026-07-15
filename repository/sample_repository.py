from models.sample import Sample
from repository.json_repository import load_json, save_json


class SampleRepository:
    def __init__(self, file_path):
        self.file_path = file_path

    def get_all(self) -> list[Sample]:
        return [Sample.from_dict(item) for item in load_json(self.file_path)]

    def get_by_id(self, sample_id: str) -> Sample | None:
        for sample in self.get_all():
            if sample.sample_id == sample_id:
                return sample
        return None

    def create(self, sample: Sample) -> Sample:
        samples = self.get_all()
        if any(s.sample_id == sample.sample_id for s in samples):
            raise ValueError(f"이미 존재하는 시료 ID입니다: {sample.sample_id}")
        samples.append(sample)
        save_json(self.file_path, [s.to_dict() for s in samples])
        return sample

    def generate_sample_id(self) -> str:
        existing_numbers = [int(s.sample_id.split("-")[1]) for s in self.get_all()]
        next_number = max(existing_numbers, default=0) + 1
        return f"S-{next_number:03d}"

    def search_by_name(self, keyword: str) -> list[Sample]:
        keyword_lower = keyword.lower()
        return [s for s in self.get_all() if keyword_lower in s.name.lower()]

    def decrease_stock(self, sample_id: str, amount: int) -> None:
        samples = self.get_all()
        for sample in samples:
            if sample.sample_id == sample_id:
                sample.stock_quantity -= amount
        save_json(self.file_path, [s.to_dict() for s in samples])
