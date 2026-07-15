from controllers.monitoring_controller import MonitoringController
from models.order import Order
from models.sample import Sample
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository


def make_controller(tmp_path):
    sample_repo = SampleRepository(tmp_path / "samples.json")
    order_repo = OrderRepository(tmp_path / "orders.json")
    controller = MonitoringController(order_repo, sample_repo)
    return controller, order_repo, sample_repo


def add_sample(sample_repo, sample_id, stock_quantity):
    sample_repo.create(
        Sample(
            sample_id=sample_id,
            name=f"Sample-{sample_id}",
            average_production_minutes=30.0,
            yield_rate=0.9,
            stock_quantity=stock_quantity,
        )
    )


def add_order(order_repo, order_id, sample_id, quantity, status):
    order_repo.create(
        Order(
            order_id=order_id,
            sample_id=sample_id,
            customer_name="ACME Corp",
            quantity=quantity,
            status=status,
        )
    )


def test_get_order_status_counts_excludes_rejected(tmp_path):
    controller, order_repo, _ = make_controller(tmp_path)
    add_order(order_repo, "ORD-1", "S-001", 10, "RESERVED")
    add_order(order_repo, "ORD-2", "S-001", 5, "REJECTED")
    add_order(order_repo, "ORD-3", "S-001", 5, "CONFIRMED")

    counts = controller.get_order_status_counts()

    assert counts == {"RESERVED": 1, "CONFIRMED": 1, "PRODUCING": 0, "RELEASED": 0}


def test_get_order_status_counts_counts_each_status(tmp_path):
    controller, order_repo, _ = make_controller(tmp_path)
    add_order(order_repo, "ORD-1", "S-001", 10, "RESERVED")
    add_order(order_repo, "ORD-2", "S-001", 10, "RESERVED")
    add_order(order_repo, "ORD-3", "S-001", 10, "PRODUCING")
    add_order(order_repo, "ORD-4", "S-001", 10, "RELEASED")

    counts = controller.get_order_status_counts()

    assert counts == {"RESERVED": 2, "CONFIRMED": 0, "PRODUCING": 1, "RELEASED": 1}


def test_inventory_status_is_depleted_when_stock_is_zero(tmp_path):
    controller, order_repo, sample_repo = make_controller(tmp_path)
    add_sample(sample_repo, "S-001", stock_quantity=0)

    report = controller.get_inventory_status()

    assert report[0].status == "고갈"


def test_inventory_status_is_short_when_stock_below_pending_demand(tmp_path):
    controller, order_repo, sample_repo = make_controller(tmp_path)
    add_sample(sample_repo, "S-001", stock_quantity=5)
    add_order(order_repo, "ORD-1", "S-001", 10, "RESERVED")

    report = controller.get_inventory_status()

    assert report[0].pending_demand == 10
    assert report[0].status == "부족"


def test_inventory_status_is_ample_when_stock_covers_pending_demand(tmp_path):
    controller, order_repo, sample_repo = make_controller(tmp_path)
    add_sample(sample_repo, "S-001", stock_quantity=20)
    add_order(order_repo, "ORD-1", "S-001", 10, "RESERVED")

    report = controller.get_inventory_status()

    assert report[0].status == "여유"


def test_pending_demand_excludes_confirmed_released_and_rejected(tmp_path):
    controller, order_repo, sample_repo = make_controller(tmp_path)
    add_sample(sample_repo, "S-001", stock_quantity=20)
    add_order(order_repo, "ORD-1", "S-001", 10, "CONFIRMED")
    add_order(order_repo, "ORD-2", "S-001", 10, "RELEASED")
    add_order(order_repo, "ORD-3", "S-001", 10, "REJECTED")

    report = controller.get_inventory_status()

    assert report[0].pending_demand == 0
    assert report[0].status == "여유"


def test_pending_demand_sums_reserved_and_producing(tmp_path):
    controller, order_repo, sample_repo = make_controller(tmp_path)
    add_sample(sample_repo, "S-001", stock_quantity=20)
    add_order(order_repo, "ORD-1", "S-001", 4, "RESERVED")
    add_order(order_repo, "ORD-2", "S-001", 6, "PRODUCING")

    report = controller.get_inventory_status()

    assert report[0].pending_demand == 10
