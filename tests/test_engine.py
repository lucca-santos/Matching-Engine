import unittest
from decimal import Decimal

from matching_engine.engine import MatchingEngine
from matching_engine.orders import Side


class TestMatchingEngine(unittest.TestCase):

    def test_limit_order_without_match_goes_to_book(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=100,
        )

        self.assertEqual(
            engine.book.best_price(Side.BUY),
            Decimal("10"),
        )

    def test_market_buy_matches_best_sell_order(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("20"),
            qty=100,
        )

        trades = engine.submit_market(
            side=Side.BUY,
            qty=50,
        )

        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0].price, Decimal("20"))
        self.assertEqual(trades[0].qty, 50)

        remaining_order = engine.book.best_order(Side.SELL)

        self.assertEqual(remaining_order.qty, 50)

    def test_market_buy_matches_multiple_sell_orders(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("20"),
            qty=100,
        )

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("20"),
            qty=200,
        )

        trades = engine.submit_market(
            side=Side.BUY,
            qty=150,
        )

        self.assertEqual(len(trades), 2)

        self.assertEqual(trades[0].price, Decimal("20"))
        self.assertEqual(trades[0].qty, 100)

        self.assertEqual(trades[1].price, Decimal("20"))
        self.assertEqual(trades[1].qty, 50)

        remaining_order = engine.book.best_order(Side.SELL)

        self.assertEqual(remaining_order.qty, 150)

    def test_market_sell_matches_best_buy_order(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=100,
        )

        trades = engine.submit_market(
            side=Side.SELL,
            qty=50,
        )

        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0].price, Decimal("10"))
        self.assertEqual(trades[0].qty, 50)

        remaining_order = engine.book.best_order(Side.BUY)

        self.assertEqual(remaining_order.qty, 50)

    def test_market_order_can_be_fully_executed(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("20"),
            qty=100,
        )

        trades = engine.submit_market(
            side=Side.BUY,
            qty=100,
        )

        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0].qty, 100)

        self.assertIsNone(
            engine.book.best_order(Side.SELL)
        )

    def test_market_order_matches_multiple_price_levels(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("20"),
            qty=100,
        )

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("21"),
            qty=100,
        )

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("22"),
            qty=100,
        )

        trades = engine.submit_market(
            side=Side.BUY,
            qty=250,
        )

        self.assertEqual(len(trades), 3)

        self.assertEqual(trades[0].price, Decimal("20"))
        self.assertEqual(trades[0].qty, 100)

        self.assertEqual(trades[1].price, Decimal("21"))
        self.assertEqual(trades[1].qty, 100)

        self.assertEqual(trades[2].price, Decimal("22"))
        self.assertEqual(trades[2].qty, 50)

        remaining_order = engine.book.best_order(Side.SELL)

        self.assertEqual(remaining_order.price, Decimal("22"))
        self.assertEqual(remaining_order.qty, 50)

    def test_unfilled_market_quantity_does_not_remain_in_book(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("20"),
            qty=50,
        )

        trades = engine.submit_market(
            side=Side.BUY,
            qty=100,
        )

        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0].qty, 50)

        self.assertIsNone(
            engine.book.best_order(Side.SELL)
        )

        self.assertIsNone(
            engine.book.best_order(Side.BUY)
        )

    def test_trade_has_required_output_format(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("20"),
            qty=100,
        )

        trades = engine.submit_market(
            side=Side.BUY,
            qty=50,
        )

        self.assertEqual(
            str(trades[0]),
            "Trade, price: 20, qty: 50",
        )


if __name__ == "__main__":
    unittest.main()