from __future__ import annotations

from collections import deque
from decimal import Decimal
from typing import Deque, Dict, Optional

from .orders import Order, OrderType, Side


class OrderBook:
    def __init__(self) -> None:
        self.buy_orders: Dict[Decimal, Deque[Order]] = {}
        self.sell_orders: Dict[Decimal, Deque[Order]] = {}

    def _get_side_book(self, side: Side) -> Dict[Decimal, Deque[Order]]:
        if side is Side.BUY:
            return self.buy_orders

        return self.sell_orders

    def add(self, order: Order) -> None:
        if order.type is not OrderType.LIMIT:
            raise ValueError("somente ordens limit podem permanecer no livro")

        if order.price is None:
            raise ValueError("ordem limit precisa possuir preco")

        side_book = self._get_side_book(order.side)

        if order.price not in side_book:
            side_book[order.price] = deque()

        side_book[order.price].append(order)

    def best_price(self, side: Side) -> Optional[Decimal]:
        side_book = self._get_side_book(side)

        if not side_book:
            return None

        if side is Side.BUY:
            return max(side_book)

        return min(side_book)

    def best_order(self, side: Side) -> Optional[Order]:
        price = self.best_price(side)

        if price is None:
            return None

        side_book = self._get_side_book(side)

        return side_book[price][0]

    def remove_best_order(self, side: Side) -> Optional[Order]:
        price = self.best_price(side)

        if price is None:
            return None

        side_book = self._get_side_book(side)
        orders_at_price = side_book[price]

        order = orders_at_price.popleft()

        if not orders_at_price:
            del side_book[price]

        return order