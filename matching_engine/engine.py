from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .book import OrderBook
from .orders import Order, OrderType, Side


@dataclass
class Trade:
    price: Decimal
    qty: int

    def __str__(self) -> str:
        price = f"{self.price.normalize():f}"

        return f"Trade, price: {price}, qty: {self.qty}"


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

    def submit_market(
        self,
        side: Side,
        qty: int,
    ) -> list[Trade]:

        order = Order(
            side=side,
            type=OrderType.MARKET,
            qty=qty,
        )

        opposite_side = side.opposite
        trades = []

        while order.qty > 0:

            best_order = self.book.best_order(opposite_side)

            if best_order is None:
                break

            trade_qty = min(
                order.qty,
                best_order.qty,
            )

            trade = Trade(
                price=best_order.price,
                qty=trade_qty,
            )

            trades.append(trade)

            order.qty -= trade_qty
            best_order.qty -= trade_qty

            if best_order.qty == 0:
                self.book.remove_best_order(opposite_side)

        return trades