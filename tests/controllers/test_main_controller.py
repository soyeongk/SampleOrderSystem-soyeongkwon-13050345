from controllers.main_controller import MainController
from models.order import Order
from models.production_queue_entry import ProductionQueueEntry
from models.sample import Sample
from repository.order_repository import OrderRepository
from repository.production_queue_repository import ProductionQueueRepository
from repository.sample_repository import SampleRepository


def make_paths(tmp_path):
    return (
        tmp_path / "samples.json",
        tmp_path / "orders.json",
        tmp_path / "production_queue.json",
    )


def test_build_system_status_returns_zeros_when_empty(tmp_path):
    samples_path, orders_path, queue_path = make_paths(tmp_path)
    controller = MainController(samples_path, orders_path, queue_path)

    status = controller.build_system_status()

    assert status["sample_count"] == 0
    assert status["total_stock"] == 0
    assert status["total_orders"] == 0
    assert status["waiting_production"] == 0


def test_build_system_status_counts_samples_and_sums_stock(tmp_path):
    samples_path, orders_path, queue_path = make_paths(tmp_path)
    sample_repo = SampleRepository(samples_path)
    sample_repo.create(
        Sample(
            sample_id="S-001",
            name="Wafer-A",
            average_production_minutes=30.0,
            yield_rate=0.9,
            stock_quantity=100,
        )
    )
    sample_repo.create(
        Sample(
            sample_id="S-002",
            name="Wafer-B",
            average_production_minutes=30.0,
            yield_rate=0.9,
            stock_quantity=50,
        )
    )
    controller = MainController(samples_path, orders_path, queue_path)

    status = controller.build_system_status()

    assert status["sample_count"] == 2
    assert status["total_stock"] == 150


def test_build_system_status_excludes_rejected_orders(tmp_path):
    samples_path, orders_path, queue_path = make_paths(tmp_path)
    order_repo = OrderRepository(orders_path)
    order_repo.create(
        Order(
            order_id="ORD-1",
            sample_id="S-001",
            customer_name="ACME Corp",
            quantity=10,
            status="RESERVED",
        )
    )
    order_repo.create(
        Order(
            order_id="ORD-2",
            sample_id="S-001",
            customer_name="ACME Corp",
            quantity=5,
            status="REJECTED",
        )
    )
    controller = MainController(samples_path, orders_path, queue_path)

    status = controller.build_system_status()

    assert status["total_orders"] == 1


def test_build_system_status_counts_waiting_production_queue(tmp_path):
    samples_path, orders_path, queue_path = make_paths(tmp_path)
    queue_repo = ProductionQueueRepository(queue_path)
    queue_repo.enqueue(ProductionQueueEntry(order_id="ORD-1", sample_id="S-001", quantity=10))
    queue_repo.enqueue(ProductionQueueEntry(order_id="ORD-2", sample_id="S-001", quantity=5))
    controller = MainController(samples_path, orders_path, queue_path)

    status = controller.build_system_status()

    assert status["waiting_production"] == 2
