import unittest
from decimal import Decimal

from matching_engine.cli import execute_command
from matching_engine.engine import MatchingEngine
from matching_engine.orders import Side


class TestCLI(unittest.TestCase):

    def test_limit_buy_command_adds_order_to_book(self):
        engine = MatchingEngine()

        output = execute_command(
            engine,
            "limit buy 10 100",
        )

        order = engine.book.best_order(Side.BUY)

        self.assertEqual(output, [])
        self.assertIsNotNone(order)
        self.assertEqual(order.price, Decimal("10"))
        self.assertEqual(order.qty, 100)

    def test_limit_sell_command_adds_order_to_book(self):
        engine = MatchingEngine()

        output = execute_command(
            engine,
            "limit sell 20 100",
        )

        order = engine.book.best_order(Side.SELL)

        self.assertEqual(output, [])
        self.assertIsNotNone(order)
        self.assertEqual(order.price, Decimal("20"))
        self.assertEqual(order.qty, 100)

    def test_market_buy_command_executes_trade(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("20"),
            qty=100,
        )

        output = execute_command(
            engine,
            "market buy 50",
        )

        self.assertEqual(
            output,
            ["Trade, price: 20, qty: 50"],
        )

    def test_market_sell_command_executes_trade(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=100,
        )

        output = execute_command(
            engine,
            "market sell 50",
        )

        self.assertEqual(
            output,
            ["Trade, price: 10, qty: 50"],
        )

    def test_aggressive_limit_command_returns_trade(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("20"),
            qty=100,
        )

        output = execute_command(
            engine,
            "limit buy 25 50",
        )

        self.assertEqual(
            output,
            ["Trade, price: 20, qty: 50"],
        )

    def test_invalid_command_raises_error(self):
        engine = MatchingEngine()

        with self.assertRaises(ValueError):
            execute_command(
                engine,
                "invalid command",
            )

    def test_limit_command_with_missing_arguments_raises_error(self):
        engine = MatchingEngine()

        with self.assertRaises(ValueError):
            execute_command(
                engine,
                "limit buy 10",
            )

    def test_market_command_with_missing_arguments_raises_error(self):
        engine = MatchingEngine()

        with self.assertRaises(ValueError):
            execute_command(
                engine,
                "market buy",
            )

    def test_invalid_side_raises_error(self):
        engine = MatchingEngine()

        with self.assertRaises(ValueError):
            execute_command(
                engine,
                "limit invalid 10 100",
            )

    def test_invalid_price_raises_error(self):
        engine = MatchingEngine()

        with self.assertRaises(ValueError):
            execute_command(
                engine,
                "limit buy invalid 100",
            )

    def test_invalid_quantity_raises_error(self):
        engine = MatchingEngine()

        with self.assertRaises(ValueError):
            execute_command(
                engine,
                "limit buy 10 invalid",
            )


if __name__ == "__main__":
    unittest.main()