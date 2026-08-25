from __future__ import annotations

from decimal import Decimal

from .book import OrderBook
from .orders import Order, OrderType, Side


class MatchingEngine:

    def __init__(self) -> None:
        self.book = OrderBook()

    def submit_limit(
        self,
        side: Side,
        price: Decimal,
        qty: int,
    ) -> None:

        order = Order(
            side=side,
            type=OrderType.LIMIT,
            qty=qty,
            price=price,
        )

        self.book.add(order)