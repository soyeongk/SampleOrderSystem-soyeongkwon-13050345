import pytest

from models.sample import Sample
from repository.sample_repository import SampleRepository


def make_sample(sample_id="S-001", name="Wafer-A", stock_quantity=100):
    return Sample(
        sample_id=sample_id,
        name=name,
        average_production_minutes=30.0,
        yield_rate=0.9,
        stock_quantity=stock_quantity,
    )


def test_create_persists_sample_to_json_file(tmp_path):
    file_path = tmp_path / "samples.json"
    repo = SampleRepository(file_path)

    repo.create(make_sample())

    reloaded_repo = SampleRepository(file_path)
    all_samples = reloaded_repo.get_all()

    assert len(all_samples) == 1
    assert all_samples[0].sample_id == "S-001"
    assert all_samples[0].name == "Wafer-A"


def test_create_rejects_duplicate_sample_id(tmp_path):
    file_path = tmp_path / "samples.json"
    repo = SampleRepository(file_path)
    repo.create(make_sample(sample_id="S-001"))

    with pytest.raises(ValueError):
        repo.create(make_sample(sample_id="S-001"))


def test_create_rejects_duplicate_sample_name(tmp_path):
    file_path = tmp_path / "samples.json"
    repo = SampleRepository(file_path)
    repo.create(make_sample(sample_id="S-001", name="Wafer-A"))

    with pytest.raises(ValueError):
        repo.create(make_sample(sample_id="S-002", name="Wafer-A"))


def test_get_by_id_returns_none_when_not_found(tmp_path):
    file_path = tmp_path / "samples.json"
    repo = SampleRepository(file_path)

    assert repo.get_by_id("S-999") is None


def test_generate_sample_id_returns_s001_when_empty(tmp_path):
    repo = SampleRepository(tmp_path / "samples.json")

    assert repo.generate_sample_id() == "S-001"


def test_generate_sample_id_returns_next_after_existing_max(tmp_path):
    repo = SampleRepository(tmp_path / "samples.json")
    repo.create(make_sample(sample_id="S-001", name="Wafer-A"))
    repo.create(make_sample(sample_id="S-002", name="Wafer-B"))

    assert repo.generate_sample_id() == "S-003"


def test_search_by_name_returns_matches_case_insensitive(tmp_path):
    repo = SampleRepository(tmp_path / "samples.json")
    repo.create(make_sample(sample_id="S-001", name="Silicon Wafer"))
    repo.create(make_sample(sample_id="S-002", name="GaN Epitaxial"))

    results = repo.search_by_name("wafer")

    assert len(results) == 1
    assert results[0].sample_id == "S-001"


def test_search_by_name_returns_empty_list_when_no_match(tmp_path):
    repo = SampleRepository(tmp_path / "samples.json")
    repo.create(make_sample(sample_id="S-001", name="Silicon Wafer"))

    assert repo.search_by_name("nonexistent") == []


def test_decrease_stock_reduces_and_persists(tmp_path):
    repo = SampleRepository(tmp_path / "samples.json")
    repo.create(make_sample(sample_id="S-001", stock_quantity=100))

    repo.decrease_stock("S-001", 30)

    assert repo.get_by_id("S-001").stock_quantity == 70


def test_increase_stock_increases_and_persists(tmp_path):
    repo = SampleRepository(tmp_path / "samples.json")
    repo.create(make_sample(sample_id="S-001", stock_quantity=100))

    repo.increase_stock("S-001", 50)

    assert repo.get_by_id("S-001").stock_quantity == 150
