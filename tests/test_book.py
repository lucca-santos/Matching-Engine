import unittest
from decimal import Decimal

from matching_engine.book import OrderBook
from matching_engine.orders import Order, OrderType, Side


class TestOrderBook(unittest.TestCase):

    def test_add_buy_limit_order(self):
        book = OrderBook()

        order = Order(
            side=Side.BUY,
            type=OrderType.LIMIT,
            qty=100,
            price=Decimal("10"),
        )

        book.add(order)

        self.assertIn(Decimal("10"), book.buy_orders)
        self.assertIs(
            book.buy_orders[Decimal("10")][0],
            order,
        )

    def test_add_sell_limit_order(self):
        book = OrderBook()

        order = Order(
            side=Side.SELL,
            type=OrderType.LIMIT,
            qty=100,
            price=Decimal("20"),
        )

        book.add(order)

        self.assertIn(Decimal("20"), book.sell_orders)
        self.assertIs(
            book.sell_orders[Decimal("20")][0],
            order,
        )

    def test_best_buy_price_is_highest(self):
        book = OrderBook()

        book.add(
            Order(
                side=Side.BUY,
                type=OrderType.LIMIT,
                qty=100,
                price=Decimal("9"),
            )
        )

        book.add(
            Order(
                side=Side.BUY,
                type=OrderType.LIMIT,
                qty=100,
                price=Decimal("11"),
            )
        )

        book.add(
            Order(
                side=Side.BUY,
                type=OrderType.LIMIT,
                qty=100,
                price=Decimal("10"),
            )
        )

        self.assertEqual(
            book.best_price(Side.BUY),
            Decimal("11"),
        )

    def test_best_sell_price_is_lowest(self):
        book = OrderBook()

        book.add(
            Order(
                side=Side.SELL,
                type=OrderType.LIMIT,
                qty=100,
                price=Decimal("21"),
            )
        )

        book.add(
            Order(
                side=Side.SELL,
                type=OrderType.LIMIT,
                qty=100,
                price=Decimal("19"),
            )
        )

        book.add(
            Order(
                side=Side.SELL,
                type=OrderType.LIMIT,
                qty=100,
                price=Decimal("20"),
            )
        )

        self.assertEqual(
            book.best_price(Side.SELL),
            Decimal("19"),
        )

    def test_orders_at_same_price_keep_arrival_order(self):
        book = OrderBook()

        first_order = Order(
            side=Side.SELL,
            type=OrderType.LIMIT,
            qty=100,
            price=Decimal("20"),
        )

        second_order = Order(
            side=Side.SELL,
            type=OrderType.LIMIT,
            qty=200,
            price=Decimal("20"),
        )

        book.add(first_order)
        book.add(second_order)

        self.assertIs(
            book.best_order(Side.SELL),
            first_order,
        )

    def test_remove_best_order(self):
        book = OrderBook()

        first_order = Order(
            side=Side.SELL,
            type=OrderType.LIMIT,
            qty=100,
            price=Decimal("20"),
        )

        second_order = Order(
            side=Side.SELL,
            type=OrderType.LIMIT,
            qty=200,
            price=Decimal("20"),
        )

        book.add(first_order)
        book.add(second_order)

        removed_order = book.remove_best_order(Side.SELL)

        self.assertIs(removed_order, first_order)
        self.assertIs(
            book.best_order(Side.SELL),
            second_order,
        )


if __name__ == "__main__":
    unittest.main()