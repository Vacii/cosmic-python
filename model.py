from dataclasses import dataclass
from datetime import date
from typing import List, Optional


class OutOfStock(Exception):
    pass


@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int


class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date] = None):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        # self.available_quantity = qty
        self._purchased_quantity = qty
        self._allocations = set()

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine):
        return self.sku == line.sku and self.available_quantity >= line.qty

    def __eq__(self, value):  # Sets how objects are compared
        if not isinstance(value, Batch):
            return False
        return value.reference == self.reference

    def __hash__(self):  # Needs to be set for the Id of entity
        return hash(self.reference)

    def __gt__(self, value):  # Sets how objects are compared
        if self.eta is None:
            return False
        if value.eta is None:
            return True
        return self.eta > value.eta


def allocate(line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")
