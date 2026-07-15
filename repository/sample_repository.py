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
