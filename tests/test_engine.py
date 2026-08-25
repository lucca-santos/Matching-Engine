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


    def test_limit_buy_without_crossing_remains_in_book(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("20"),
            qty=100,
        )

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=100,
        )

        self.assertEqual(
            engine.book.best_price(Side.BUY),
            Decimal("10"),
        )

        self.assertEqual(
            engine.book.best_price(Side.SELL),
            Decimal("20"),
        )

    
    def test_aggressive_limit_buy_matches_sell_order(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("20"),
            qty=100,
        )

        trades = engine.submit_limit(
            side=Side.BUY,
            price=Decimal("25"),
            qty=50,
        )

        self.assertEqual(len(trades), 1)

        self.assertEqual(
            trades[0].price,
            Decimal("20"),
        )

        self.assertEqual(
            trades[0].qty,
            50,
        )

        remaining_sell = engine.book.best_order(Side.SELL)

        self.assertEqual(
            remaining_sell.qty,
            50,
        )

        self.assertIsNone(
            engine.book.best_order(Side.BUY)
        )


    def test_aggressive_limit_sell_matches_buy_order(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("20"),
            qty=100,
        )         

        trades = engine.submit_limit(
            side=Side.SELL,
            price=Decimal("15"),
            qty=50,
        )

        self.assertEqual(len(trades), 1)

        self.assertEqual(
            trades[0].price,
            Decimal("20"),
        )

        self.assertEqual(
            trades[0].qty,
            50,
        )

        remaining_buy = engine.book.best_order(Side.BUY)

        self.assertEqual(
            remaining_buy.qty,
            50,
            )

        self.assertIsNone(
            engine.book.best_order(Side.SELL)
        )


    def test_limit_buy_respects_price_limit(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("19"),
            qty=50,
        )

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("20"),
            qty=50,
        )

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("21"),
            qty=50,
        )

        trades = engine.submit_limit(
            side=Side.BUY,
            price=Decimal("20"),
            qty=120,
        )

        self.assertEqual(len(trades), 2)

        self.assertEqual(trades[0].price, Decimal("19"))
        self.assertEqual(trades[0].qty, 50)

        self.assertEqual(trades[1].price, Decimal("20"))
        self.assertEqual(trades[1].qty, 50)

        self.assertEqual(
            engine.book.best_price(Side.SELL),
            Decimal("21"),
        )


    def test_remaining_limit_quantity_stays_in_book(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("20"),
            qty=100,
        )

        trades = engine.submit_limit(
            side=Side.BUY,
            price=Decimal("25"),
            qty=150,
        )

        self.assertEqual(len(trades), 1)

        self.assertEqual(
            trades[0].price,
            Decimal("20"),
        )

        self.assertEqual(
            trades[0].qty,
            100,
        )

        remaining_buy = engine.book.best_order(Side.BUY)

        self.assertIsNotNone(remaining_buy)

        self.assertEqual(
            remaining_buy.price,
            Decimal("25"),
        )

        self.assertEqual(
            remaining_buy.qty,
            50,
        )

        self.assertIsNone(
            engine.book.best_order(Side.SELL)
        )

if __name__ == "__main__":
    unittest.main()