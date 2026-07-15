import pytest

from models.order import Order
from repository.order_repository import OrderRepository


def make_order(order_id="ORD-20260715-1000-01"):
    return Order(
        order_id=order_id,
        sample_id="S-001",
        customer_name="ACME Corp",
        quantity=10,
        status="RESERVED",
    )


def test_create_persists_order_to_json_file(tmp_path):
    file_path = tmp_path / "orders.json"
    repo = OrderRepository(file_path)

    repo.create(make_order())

    reloaded_repo = OrderRepository(file_path)
    all_orders = reloaded_repo.get_all()

    assert len(all_orders) == 1
    assert all_orders[0].order_id == "ORD-20260715-1000-01"
    assert all_orders[0].status == "RESERVED"


def test_create_rejects_duplicate_order_id(tmp_path):
    file_path = tmp_path / "orders.json"
    repo = OrderRepository(file_path)
    repo.create(make_order(order_id="ORD-20260715-1000-01"))

    with pytest.raises(ValueError):
        repo.create(make_order(order_id="ORD-20260715-1000-01"))


def test_generate_order_id_has_no_collision_with_existing(tmp_path):
    from datetime import datetime

    repo = OrderRepository(tmp_path / "orders.json")
    fixed_time = datetime(2026, 7, 15, 10, 0)
    repo.create(
        Order(
            order_id=repo.generate_order_id(fixed_time),
            sample_id="S-001",
            customer_name="ACME Corp",
            quantity=10,
            status="RESERVED",
        )
    )

    second_id = repo.generate_order_id(fixed_time)

    assert second_id == "ORD-20260715-1000-02"


def test_update_status_changes_and_persists(tmp_path):
    repo = OrderRepository(tmp_path / "orders.json")
    repo.create(make_order(order_id="ORD-20260715-1000-01"))

    repo.update_status("ORD-20260715-1000-01", "CONFIRMED")

    reloaded = OrderRepository(tmp_path / "orders.json")
    orders = reloaded.get_all()
    assert orders[0].status == "CONFIRMED"
