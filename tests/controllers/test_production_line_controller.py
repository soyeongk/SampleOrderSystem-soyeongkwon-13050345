from datetime import datetime, timedelta

from controllers.production_line_controller import ProductionLineController
from models.order import Order
from models.production_queue_entry import ProductionQueueEntry
from models.sample import Sample
from repository.order_repository import OrderRepository
from repository.production_queue_repository import ProductionQueueRepository
from repository.sample_repository import SampleRepository

NOW = datetime(2026, 7, 15, 10, 0)


def make_env(tmp_path, stock_quantity=5, yield_rate=0.1, average_production_minutes=1.0):
    sample_repo = SampleRepository(tmp_path / "samples.json")
    sample_repo.create(
        Sample(
            sample_id="S-001",
            name="Wafer-A",
            average_production_minutes=average_production_minutes,
            yield_rate=yield_rate,
            stock_quantity=stock_quantity,
        )
    )
    order_repo = OrderRepository(tmp_path / "orders.json")
    queue_repo = ProductionQueueRepository(tmp_path / "production_queue.json")
    controller = ProductionLineController(order_repo, sample_repo, queue_repo)
    return controller, order_repo, sample_repo, queue_repo


def add_order(order_repo, order_id, quantity, status="PRODUCING"):
    order_repo.create(
        Order(
            order_id=order_id,
            sample_id="S-001",
            customer_name="ACME Corp",
            quantity=quantity,
            status=status,
        )
    )


def test_advance_does_nothing_when_queue_empty(tmp_path):
    controller, _, sample_repo, _ = make_env(tmp_path)

    controller.advance(NOW)

    assert sample_repo.get_by_id("S-001").stock_quantity == 5


def test_advance_starts_production_when_stock_insufficient(tmp_path):
    controller, order_repo, sample_repo, queue_repo = make_env(tmp_path, stock_quantity=5)
    add_order(order_repo, "ORD-1", quantity=10)
    queue_repo.enqueue(ProductionQueueEntry(order_id="ORD-1", sample_id="S-001", quantity=10))

    controller.advance(NOW)

    entry = queue_repo.get_all()[0]
    assert entry.started_at == NOW.isoformat()
    assert entry.shortfall_quantity == 5
    assert entry.actual_quantity == 50
    assert entry.total_production_minutes == 50.0
    assert sample_repo.get_by_id("S-001").stock_quantity == 5
    assert order_repo.get_all()[0].status == "PRODUCING"


def test_advance_resolves_immediately_when_stock_already_sufficient(tmp_path):
    controller, order_repo, sample_repo, queue_repo = make_env(tmp_path, stock_quantity=100)
    add_order(order_repo, "ORD-1", quantity=20)
    queue_repo.enqueue(ProductionQueueEntry(order_id="ORD-1", sample_id="S-001", quantity=20))

    controller.advance(NOW)

    assert queue_repo.get_all() == []
    assert order_repo.get_all()[0].status == "CONFIRMED"
    assert sample_repo.get_by_id("S-001").stock_quantity == 80


def test_advance_keeps_producing_when_elapsed_time_insufficient(tmp_path):
    controller, order_repo, sample_repo, queue_repo = make_env(tmp_path, stock_quantity=5)
    add_order(order_repo, "ORD-1", quantity=10)
    queue_repo.enqueue(ProductionQueueEntry(order_id="ORD-1", sample_id="S-001", quantity=10))
    controller.advance(NOW)  # starts production (total_production_minutes = 50)

    controller.advance(NOW + timedelta(minutes=30))

    assert len(queue_repo.get_all()) == 1
    assert order_repo.get_all()[0].status == "PRODUCING"
    assert sample_repo.get_by_id("S-001").stock_quantity == 5


def test_advance_completes_when_elapsed_time_sufficient(tmp_path):
    controller, order_repo, sample_repo, queue_repo = make_env(tmp_path, stock_quantity=5)
    add_order(order_repo, "ORD-1", quantity=10)
    queue_repo.enqueue(ProductionQueueEntry(order_id="ORD-1", sample_id="S-001", quantity=10))
    controller.advance(NOW)  # starts production (actual=50, total_production_minutes=50)

    controller.advance(NOW + timedelta(minutes=50))

    assert queue_repo.get_all() == []
    assert order_repo.get_all()[0].status == "CONFIRMED"
    assert sample_repo.get_by_id("S-001").stock_quantity == 45


def test_advance_cascades_to_next_entry_without_extra_production(tmp_path):
    controller, order_repo, sample_repo, queue_repo = make_env(tmp_path, stock_quantity=5)
    add_order(order_repo, "ORD-1", quantity=10)
    add_order(order_repo, "ORD-2", quantity=30)
    queue_repo.enqueue(ProductionQueueEntry(order_id="ORD-1", sample_id="S-001", quantity=10))
    queue_repo.enqueue(ProductionQueueEntry(order_id="ORD-2", sample_id="S-001", quantity=30))
    controller.advance(NOW)  # starts ORD-1 production only (ORD-2 stays queued, untouched)

    controller.advance(NOW + timedelta(minutes=50))  # ORD-1 completes; ORD-2 resolves via leftover

    assert queue_repo.get_all() == []
    statuses = {o.order_id: o.status for o in order_repo.get_all()}
    assert statuses == {"ORD-1": "CONFIRMED", "ORD-2": "CONFIRMED"}
    assert sample_repo.get_by_id("S-001").stock_quantity == 15


def test_get_current_status_returns_none_when_queue_empty(tmp_path):
    controller, *_ = make_env(tmp_path)

    assert controller.get_current_status(NOW) is None


def test_get_current_status_returns_head_entry_after_advancing(tmp_path):
    controller, order_repo, _, queue_repo = make_env(tmp_path, stock_quantity=5)
    add_order(order_repo, "ORD-1", quantity=10)
    queue_repo.enqueue(ProductionQueueEntry(order_id="ORD-1", sample_id="S-001", quantity=10))

    status = controller.get_current_status(NOW)

    assert status.order_id == "ORD-1"
    assert status.actual_quantity == 50


def test_get_waiting_queue_excludes_head(tmp_path):
    controller, order_repo, _, queue_repo = make_env(tmp_path, stock_quantity=5)
    add_order(order_repo, "ORD-1", quantity=10)
    add_order(order_repo, "ORD-2", quantity=30)
    queue_repo.enqueue(ProductionQueueEntry(order_id="ORD-1", sample_id="S-001", quantity=10))
    queue_repo.enqueue(ProductionQueueEntry(order_id="ORD-2", sample_id="S-001", quantity=30))

    waiting = controller.get_waiting_queue()

    assert [e.order_id for e in waiting] == ["ORD-2"]
