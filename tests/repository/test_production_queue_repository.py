from models.production_queue_entry import ProductionQueueEntry
from repository.production_queue_repository import ProductionQueueRepository


def make_entry(order_id, sample_id="S-001", shortfall_quantity=10):
    return ProductionQueueEntry(
        order_id=order_id,
        sample_id=sample_id,
        shortfall_quantity=shortfall_quantity,
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
