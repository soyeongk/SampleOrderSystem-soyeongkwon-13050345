from controllers.sample_controller import SampleController
from models.sample import Sample
from repository.sample_repository import SampleRepository


class FakeSampleView:
    def __init__(self, new_sample_input=None, lookup_choice=None, search_keyword=None):
        self._new_sample_input = new_sample_input
        self._lookup_choice = lookup_choice
        self._search_keyword = search_keyword
        self.registration_successes = []
        self.registration_errors = []
        self.displayed_sample_lists = []

    def show_registration_menu(self):
        pass

    def read_new_sample_input(self):
        return self._new_sample_input

    def show_registration_success(self, sample):
        self.registration_successes.append(sample)

    def show_registration_error(self, message):
        self.registration_errors.append(message)

    def show_lookup_menu(self):
        pass

    def read_lookup_choice(self):
        return self._lookup_choice

    def read_search_keyword(self):
        return self._search_keyword

    def show_sample_list(self, samples):
        self.displayed_sample_lists.append(samples)


def make_controller(repo_path, **view_kwargs):
    repo = SampleRepository(repo_path)
    view = FakeSampleView(**view_kwargs)
    return SampleController(repo, view), repo, view


def test_register_sample_creates_sample_with_generated_id(tmp_path):
    controller, repo, view = make_controller(
        tmp_path / "samples.json",
        new_sample_input={
            "name": "Wafer-A",
            "average_production_minutes": "30",
            "yield_rate": "0.9",
            "stock_quantity": "100",
        },
    )

    controller.register_sample()

    all_samples = repo.get_all()
    assert len(all_samples) == 1
    assert all_samples[0].sample_id == "S-001"
    assert view.registration_successes[0].sample_id == "S-001"


def test_register_sample_rejects_empty_name(tmp_path):
    controller, repo, view = make_controller(
        tmp_path / "samples.json",
        new_sample_input={
            "name": "",
            "average_production_minutes": "30",
            "yield_rate": "0.9",
            "stock_quantity": "100",
        },
    )

    controller.register_sample()

    assert repo.get_all() == []
    assert len(view.registration_errors) == 1


def test_register_sample_rejects_non_numeric_input(tmp_path):
    controller, repo, view = make_controller(
        tmp_path / "samples.json",
        new_sample_input={
            "name": "Wafer-A",
            "average_production_minutes": "abc",
            "yield_rate": "0.9",
            "stock_quantity": "100",
        },
    )

    controller.register_sample()

    assert repo.get_all() == []
    assert len(view.registration_errors) == 1


def test_register_sample_rejects_yield_rate_out_of_range(tmp_path):
    controller, repo, view = make_controller(
        tmp_path / "samples.json",
        new_sample_input={
            "name": "Wafer-A",
            "average_production_minutes": "30",
            "yield_rate": "1.5",
            "stock_quantity": "100",
        },
    )

    controller.register_sample()

    assert repo.get_all() == []
    assert len(view.registration_errors) == 1


def test_browse_samples_shows_full_list_when_choice_is_1(tmp_path):
    controller, repo, view = make_controller(tmp_path / "samples.json", lookup_choice="1")
    repo.create(
        Sample(
            sample_id="S-001",
            name="Wafer-A",
            average_production_minutes=30.0,
            yield_rate=0.9,
            stock_quantity=100,
        )
    )

    controller.browse_samples()

    assert len(view.displayed_sample_lists[0]) == 1


def test_browse_samples_shows_search_result_when_choice_is_2(tmp_path):
    controller, repo, view = make_controller(
        tmp_path / "samples.json", lookup_choice="2", search_keyword="Wafer"
    )

    repo.create(
        Sample(
            sample_id="S-001",
            name="Silicon Wafer",
            average_production_minutes=30.0,
            yield_rate=0.9,
            stock_quantity=100,
        )
    )
    repo.create(
        Sample(
            sample_id="S-002",
            name="GaN Epitaxial",
            average_production_minutes=30.0,
            yield_rate=0.9,
            stock_quantity=100,
        )
    )

    controller.browse_samples()

    assert len(view.displayed_sample_lists[0]) == 1
    assert view.displayed_sample_lists[0][0].sample_id == "S-001"
