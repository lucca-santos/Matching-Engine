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

        self.assertEqual(
            output,
            ["Order created: buy 100 @ 10 ord-1"],
        )
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

        self.assertEqual(
            output,
            ["Order created: sell 100 @ 20 ord-1"],
        )
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


    def test_print_book_command(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=200,
        )

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("9.99"),
            qty=100,
        )

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("10.5"),
            qty=100,
        )

        output = execute_command(
            engine,
            "print book",
        )

        self.assertEqual(
            output,
            [
                "Ordens de Compra    | Ordens de Venda",
                "--------------------|--------------------",
                "200 @ 10            | 100 @ 10.5",
                "100 @ 9.99          |",
            ],
        )
        
    
    def test_cancel_order_command(self):
        engine = MatchingEngine()

        execute_command(
            engine,
            "limit buy 10 100",
        )

        order = engine.book.best_order(Side.BUY)

        output = execute_command(
            engine,
            f"cancel order {order.order_id}",
        )

        self.assertEqual(
            output,
            ["Order cancelled"],
        )

        self.assertIsNone(
            engine.book.find_order(order.order_id)
        )


    def test_modify_order_price_command(self):
        engine = MatchingEngine()

        execute_command(
            engine,
            "limit buy 10 100",
        )

        order = engine.book.best_order(Side.BUY)

        output = execute_command(
            engine,
            f"modify order {order.order_id} price 9.98",
        )

        self.assertEqual(
            output,
            ["Order modified"],
        )

        modified_order = engine.book.find_order(
            order.order_id
        )

        self.assertEqual(
            modified_order.price,
            Decimal("9.98"),
        )


    def test_modify_order_price_and_quantity_command(self):
        engine = MatchingEngine()

        execute_command(
            engine,
            "limit buy 10 100",
        )

        order = engine.book.best_order(Side.BUY)

        output = execute_command(
            engine,
            f"modify order {order.order_id} price 9.98 qty 50",
        )

        self.assertEqual(
            output,
            ["Order modified"],
        )

        modified_order = engine.book.find_order(
            order.order_id
        )

        self.assertEqual(
            modified_order.price,
            Decimal("9.98"),
        )

        self.assertEqual(
            modified_order.qty,
            50,
        )
    
    
    def test_peg_bid_command(self):
        engine = MatchingEngine()

        execute_command(
            engine,
            "limit buy 10 200",
        )

        output = execute_command(
            engine,
            "peg bid buy 150",
        )

        self.assertEqual(
            output,
            [
                "Order created: buy 150 @ 10 ord-2"
            ],
        )

        peg_order = engine.book.find_order(
            "ord-2"
        )

        self.assertIsNotNone(peg_order)

        self.assertEqual(
            peg_order.price,
            Decimal("10"),
        )


    def test_peg_offer_command(self):
        engine = MatchingEngine()

        execute_command(
            engine,
            "limit sell 10.5 100",
        )

        output = execute_command(
            engine,
            "peg offer sell 150",
        )

        self.assertEqual(
            output,
            [
                "Order created: sell 150 @ 10.5 ord-2"
            ],
        )

        peg_order = engine.book.find_order(
            "ord-2"
        )

        self.assertIsNotNone(peg_order)

        self.assertEqual(
            peg_order.price,
            Decimal("10.5"),
        )


    def test_peg_command_without_reference_raises_error(self):
        engine = MatchingEngine()

        with self.assertRaisesRegex(
            ValueError,
            "reference price unavailable",
        ):
            execute_command(
                engine,
                "peg bid buy 100",
            )


    def test_peg_bid_reproduces_problem_example(self):
        engine = MatchingEngine()

        execute_command(
            engine,
            "limit buy 10 200",
        )

        execute_command(
            engine,
            "limit buy 9.99 100",
        )

        execute_command(
            engine,
            "limit sell 10.5 100",
        )

        execute_command(
            engine,
            "peg bid buy 150",
        )

        execute_command(
            engine,
            "limit buy 10.1 300",
        )

        output = execute_command(
            engine,
            "print book",
        )

        self.assertEqual(
            output,
            [
                "Ordens de Compra    | Ordens de Venda",
                "--------------------|--------------------",
                "150 @ 10.1          | 100 @ 10.5",
                "300 @ 10.1          |",
                "200 @ 10            |",
                "100 @ 9.99          |",
            ],
        )
    
    
    def test_cli_create_peg_offer_sell(self):
        engine = MatchingEngine()

        execute_command(
            engine,
            "limit sell 10 100",
        )

        output = execute_command(
            engine,
            "peg offer sell 50",
        )

        self.assertEqual(
            output,
            [
                "Order created: sell 50 @ 10 ord-2"
            ],
        )


    def test_cli_peg_offer_sell_updates_book(self):
        engine = MatchingEngine()

        execute_command(
            engine,
            "limit sell 10 100",
        )

        execute_command(
            engine,
            "peg offer sell 50",
        )

        execute_command(
            engine,
            "limit sell 9 100",
        )

        book = execute_command(
            engine,
            "print book",
        )

        self.assertTrue(
            any("50 @ 9" in line for line in book)
        )


    def test_cli_peg_offer_sell_without_reference(self):
        engine = MatchingEngine()

        with self.assertRaises(ValueError):
            execute_command(
                engine,
                "peg offer sell 50",
            )
    
if __name__ == "__main__":
    unittest.main()