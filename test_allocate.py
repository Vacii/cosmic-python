from datetime import date, timedelta
import pytest

from model import Batch, OrderLine, OutOfStock, allocate

# from model import ...

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefets_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 20, eta=None)
    shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 20, tomorrow)
    line = OrderLine("order-001", "RETRO-CLOCK", 3)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 17
    assert shipment_batch.available_quantity == 20


def test_prefers_earlier_batches():
    earliest_shipment_batch = Batch("earliest_shipment_batch", "RETRO-CLOCK", 20, today)
    tomorrow_shipment_batch = Batch(
        "tomorrow_shipment_batch", "RETRO-CLOCK", 20, tomorrow
    )
    later_shipment_batch = Batch("later_shipment_batch", "RETRO-CLOCK", 20, later)

    line = OrderLine("order1", "RETRO-CLOCK", 2)

    allocate(
        line, [tomorrow_shipment_batch, earliest_shipment_batch, later_shipment_batch]
    )

    assert earliest_shipment_batch.available_quantity == 18
    assert tomorrow_shipment_batch.available_quantity == 20
    assert later_shipment_batch.available_quantity == 20


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 20, eta=None)
    shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 20, tomorrow)
    line = OrderLine("order-001", "RETRO-CLOCK", 3)

    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch("batch1", "SMALL-FORK", 10, eta=today)
    allocate(OrderLine("order1", "SMALL-FORK", 10), [batch])

    with pytest.raises(OutOfStock, match="SMALL-FORK"):
        allocate(OrderLine("order2", "SMALL-FORK", 1), [batch])
