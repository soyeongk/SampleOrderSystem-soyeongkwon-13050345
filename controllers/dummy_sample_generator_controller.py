import random

from models.sample import Sample
from repository.sample_repository import SampleRepository

SAMPLE_NAMES = [
    "실리콘 웨이퍼-8인치",
    "실리콘 웨이퍼-12인치",
    "GaN 에피택셜-4인치",
    "SiC 기판-6인치",
    "InP 웨이퍼-3인치",
    "사파이어 기판-2인치",
    "게르마늄 웨이퍼-4인치",
    "석영 기판-6인치",
    "실리콘 카바이드 잉곳-8인치",
    "질화갈륨 템플릿-6인치",
]


class DummySampleGeneratorController:
    def __init__(self, sample_repository: SampleRepository, dummy_data_view):
        self.sample_repository = sample_repository
        self.dummy_data_view = dummy_data_view

    def generate_samples(self, count: int) -> list[Sample]:
        existing_names = {s.name for s in self.sample_repository.get_all()}
        created = []
        for _ in range(count):
            name = self._generate_unique_name(existing_names)
            existing_names.add(name)
            sample = Sample(
                sample_id=self.sample_repository.generate_sample_id(),
                name=name,
                average_production_minutes=round(random.uniform(0.2, 5.0), 2),
                yield_rate=round(random.uniform(0.75, 0.98), 3),
                stock_quantity=random.randint(0, 500),
            )
            self.sample_repository.create(sample)
            created.append(sample)
        return created

    def _generate_unique_name(self, existing_names: set) -> str:
        base_name = random.choice(SAMPLE_NAMES)
        if base_name not in existing_names:
            return base_name

        suffix = 2
        while f"{base_name} #{suffix}" in existing_names:
            suffix += 1
        return f"{base_name} #{suffix}"

    def handle_menu(self) -> None:
        raw_count = self.dummy_data_view.read_sample_count()
        try:
            count = int(raw_count)
        except ValueError:
            self.dummy_data_view.show_error("숫자를 입력해야 합니다.")
            return

        if count <= 0:
            self.dummy_data_view.show_error("1 이상의 개수를 입력해야 합니다.")
            return

        created = self.generate_samples(count)
        self.dummy_data_view.show_result(created)
