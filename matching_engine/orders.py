from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional

class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"

    @property
    def opposite(self) -> "Side":
        return Side.SELL if self is Side.BUY else Side.BUY

class OrderType(str, Enum):
    LIMIT = "limit"
    MARKET = "market"

@dataclass
class Order:
    side: Side
    type: OrderType
    qty: int
    price: Optional[Decimal] = None