from controllers.dummy_sample_generator_controller import DummySampleGeneratorController
from repository.sample_repository import SampleRepository


class FakeDummyDataView:
    def __init__(self, count=None):
        self._count = count
        self.results = []
        self.errors = []

    def read_sample_count(self):
        return self._count

    def show_result(self, created_samples):
        self.results.append(created_samples)

    def show_error(self, message):
        self.errors.append(message)


def make_controller(tmp_path, **view_kwargs):
    repo = SampleRepository(tmp_path / "samples.json")
    view = FakeDummyDataView(**view_kwargs)
    return DummySampleGeneratorController(repo, view), repo, view


def test_generate_samples_creates_requested_count(tmp_path):
    controller, repo, _ = make_controller(tmp_path)

    created = controller.generate_samples(5)

    assert len(created) == 5
    assert len(repo.get_all()) == 5


def test_generate_samples_continues_id_numbering_from_existing_max(tmp_path):
    controller, repo, _ = make_controller(tmp_path)
    controller.generate_samples(2)

    more = controller.generate_samples(3)

    all_ids = sorted(s.sample_id for s in repo.get_all())
    assert all_ids == ["S-001", "S-002", "S-003", "S-004", "S-005"]
    assert sorted(s.sample_id for s in more) == ["S-003", "S-004", "S-005"]


def test_generate_samples_values_within_expected_ranges(tmp_path):
    controller, repo, _ = make_controller(tmp_path)

    created = controller.generate_samples(20)

    for sample in created:
        assert 0 <= sample.yield_rate <= 1
        assert sample.stock_quantity >= 0
        assert sample.average_production_minutes > 0


def test_generate_samples_produces_unique_names_even_when_count_exceeds_name_pool(tmp_path):
    controller, repo, _ = make_controller(tmp_path)

    created = controller.generate_samples(15)

    names = [s.name for s in created]
    assert len(set(names)) == len(names)


def test_handle_menu_creates_samples_and_shows_result(tmp_path):
    controller, repo, view = make_controller(tmp_path, count="4")

    controller.handle_menu()

    assert len(repo.get_all()) == 4
    assert len(view.results[0]) == 4
    assert view.errors == []


def test_handle_menu_rejects_non_numeric_count(tmp_path):
    controller, repo, view = make_controller(tmp_path, count="abc")

    controller.handle_menu()

    assert repo.get_all() == []
    assert len(view.errors) == 1


def test_handle_menu_rejects_non_positive_count(tmp_path):
    controller, repo, view = make_controller(tmp_path, count="0")

    controller.handle_menu()

    assert repo.get_all() == []
    assert len(view.errors) == 1
