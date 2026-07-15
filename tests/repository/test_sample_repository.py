import pytest

from models.sample import Sample
from repository.sample_repository import SampleRepository


def make_sample(sample_id="S-001", stock_quantity=100):
    return Sample(
        sample_id=sample_id,
        name="Wafer-A",
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


def test_get_by_id_returns_none_when_not_found(tmp_path):
    file_path = tmp_path / "samples.json"
    repo = SampleRepository(file_path)

    assert repo.get_by_id("S-999") is None
