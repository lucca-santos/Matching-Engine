import unittest
from decimal import Decimal

from matching_engine import engine
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


if __name__ == "__main__":
    unittest.main()