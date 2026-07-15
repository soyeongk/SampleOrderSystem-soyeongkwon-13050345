from controllers.pagination import paginate
from models.sample import Sample
from repository.sample_repository import SampleRepository


class SampleController:
    def __init__(self, sample_repository: SampleRepository, sample_view):
        self.sample_repository = sample_repository
        self.sample_view = sample_view

    def register_sample(self) -> None:
        self.sample_view.show_registration_menu()
        raw_input_values = self.sample_view.read_new_sample_input()

        if not raw_input_values["name"]:
            self.sample_view.show_registration_error("시료 이름은 비어 있을 수 없습니다.")
            return

        try:
            average_production_minutes = float(raw_input_values["average_production_minutes"])
            yield_rate = float(raw_input_values["yield_rate"])
            stock_quantity = int(raw_input_values["stock_quantity"])
        except ValueError:
            self.sample_view.show_registration_error("숫자 입력값이 올바르지 않습니다.")
            return

        if not (0 <= yield_rate <= 1):
            self.sample_view.show_registration_error("수율은 0에서 1 사이여야 합니다.")
            return

        sample = Sample(
            sample_id=self.sample_repository.generate_sample_id(),
            name=raw_input_values["name"],
            average_production_minutes=average_production_minutes,
            yield_rate=yield_rate,
            stock_quantity=stock_quantity,
        )
        self.sample_repository.create(sample)
        self.sample_view.show_registration_success(sample)

    def browse_samples(self) -> None:
        self.sample_view.show_lookup_menu()
        choice = self.sample_view.read_lookup_choice()

        if choice == "1":
            samples = self.sample_repository.get_all()
        elif choice == "2":
            keyword = self.sample_view.read_search_keyword()
            samples = self.sample_repository.search_by_name(keyword)
        else:
            samples = []

        page_number = 1
        while True:
            page = paginate(samples, page_number)
            self.sample_view.show_sample_page(page)
            command = self.sample_view.read_sample_browse_command()

            if command == "n":
                page_number += 1
            elif command == "p":
                page_number -= 1
            elif command == "b":
                return
