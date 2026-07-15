from models.production_queue_entry import ProductionQueueEntry
from repository.production_queue_repository import ProductionQueueRepository


def make_entry(order_id, sample_id="S-001", quantity=10):
    return ProductionQueueEntry(
        order_id=order_id,
        sample_id=sample_id,
        quantity=quantity,
    )


def test_enqueue_persists_entry(tmp_path):
    repo = ProductionQueueRepository(tmp_path / "production_queue.json")

    repo.enqueue(make_entry("ORD-1"))

    reloaded = ProductionQueueRepository(tmp_path / "production_queue.json")
    entries = reloaded.get_all()
    assert len(entries) == 1
    assert entries[0].order_id == "ORD-1"


def test_get_all_preserves_fifo_order(tmp_path):
    repo = ProductionQueueRepository(tmp_path / "production_queue.json")
    repo.enqueue(make_entry("ORD-1"))
    repo.enqueue(make_entry("ORD-2"))
    repo.enqueue(make_entry("ORD-3"))

    entries = repo.get_all()

    assert [e.order_id for e in entries] == ["ORD-1", "ORD-2", "ORD-3"]


def test_update_entry_changes_fields_and_persists(tmp_path):
    repo = ProductionQueueRepository(tmp_path / "production_queue.json")
    repo.enqueue(make_entry("ORD-1", quantity=20))

    repo.update_entry(
        "ORD-1", started_at="2026-07-15T10:00:00", shortfall_quantity=15,
        actual_quantity=17, total_production_minutes=90.0,
    )

    reloaded = ProductionQueueRepository(tmp_path / "production_queue.json").get_all()
    assert reloaded[0].started_at == "2026-07-15T10:00:00"
    assert reloaded[0].shortfall_quantity == 15
    assert reloaded[0].actual_quantity == 17
    assert reloaded[0].total_production_minutes == 90.0


def test_remove_deletes_entry_and_persists(tmp_path):
    repo = ProductionQueueRepository(tmp_path / "production_queue.json")
    repo.enqueue(make_entry("ORD-1"))
    repo.enqueue(make_entry("ORD-2"))

    repo.remove("ORD-1")

    reloaded = ProductionQueueRepository(tmp_path / "production_queue.json").get_all()
    assert [e.order_id for e in reloaded] == ["ORD-2"]
