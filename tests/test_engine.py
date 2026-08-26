import unittest
from decimal import Decimal

from matching_engine import engine
from matching_engine.engine import MatchingEngine
from matching_engine.orders import OrderType, PegReference, Side


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


    def test_original_problem_example(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=100,
        )

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

        self.assertEqual(
            sum(trade.qty for trade in trades),
            150,
        )

        self.assertTrue(
            all(trade.price == Decimal("20") for trade in trades)
        )

        trades = engine.submit_market(
            side=Side.BUY,
            qty=200,
        )

        self.assertEqual(
            sum(trade.qty for trade in trades),
            150,
        )

        self.assertTrue(
            all(trade.price == Decimal("20") for trade in trades)
        )   

        trades = engine.submit_market(
            side=Side.SELL,
            qty=200,
        )

        self.assertEqual(
            sum(trade.qty for trade in trades),
            100,
        )

        self.assertTrue(
            all(trade.price == Decimal("10") for trade in trades)
        )


    def test_limit_orders_receive_unique_ids(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=100,
        )

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("9"),
            qty=200,
        )

        first_order = engine.book.buy_orders[Decimal("10")][0]
        second_order = engine.book.buy_orders[Decimal("9")][0]

        self.assertEqual(first_order.order_id, "ord-1")
        self.assertEqual(second_order.order_id, "ord-2")


    def test_find_order_by_id(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=100,
        )

        order = engine.book.best_order(Side.BUY)

        found_order = engine.book.find_order(order.order_id)

        self.assertIs(found_order, order)


    def test_cancel_order_removes_order_from_book(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=100,
        )

        order = engine.book.best_order(Side.BUY)

        engine.cancel_order(order.order_id)

        self.assertIsNone(
            engine.book.find_order(order.order_id)
        )


    def test_modify_price_repositions_order(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=200,
        )

        first_order = engine.book.best_order(Side.BUY)
        first_id = first_order.order_id

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("9.99"),
            qty=100,
        )

        second_order = engine.book.buy_orders[Decimal("9.99")][0]
        second_id = second_order.order_id

        engine.modify_order(
            first_id,
            price=Decimal("9.98"),
        )

        self.assertEqual(
            engine.book.best_order(Side.BUY).order_id,
            second_id,
        )

        modified_order = engine.book.find_order(first_id)

        self.assertEqual(
            modified_order.price,
            Decimal("9.98"),
        )


    def test_reduce_quantity_keeps_priority(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=100,
        )

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=200,
        )

        first_order = engine.book.buy_orders[Decimal("10")][0]
        first_id = first_order.order_id

        engine.modify_order(
            first_id,
            qty=50,
        )

        orders = engine.book.buy_orders[Decimal("10")]

        self.assertEqual(orders[0].order_id, first_id)
        self.assertEqual(orders[0].qty, 50)


    def test_increase_quantity_loses_priority(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=100,
        )

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=200,
        )

        first_order = engine.book.buy_orders[Decimal("10")][0]
        second_order = engine.book.buy_orders[Decimal("10")][1]

        first_id = first_order.order_id
        second_id = second_order.order_id

        engine.modify_order(
            first_id,
            qty=150,
        )

        orders = engine.book.buy_orders[Decimal("10")]

        self.assertEqual(orders[0].order_id, second_id)
        self.assertEqual(orders[1].order_id, first_id)


    def test_modify_price_can_generate_trade(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("10.5"),
            qty=100,
        )

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=200,
        )

        buy_order = engine.book.best_order(Side.BUY)
        buy_id = buy_order.order_id

        trades = engine.modify_order(
            buy_id,
            price=Decimal("11"),
        )

        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0].price, Decimal("10.5"))
        self.assertEqual(trades[0].qty, 100)

        remaining_order = engine.book.find_order(buy_id)

        self.assertIsNotNone(remaining_order)
        self.assertEqual(remaining_order.price, Decimal("11"))
        self.assertEqual(remaining_order.qty, 100)
        
        
    def test_peg_bid_uses_best_bid_price(self):
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

        engine.submit_peg(
            reference=PegReference.BID,
            side=Side.BUY,
            qty=150,
        )

        peg_order = engine.last_created_order

        self.assertEqual(peg_order.type, OrderType.PEG)
        self.assertEqual(
            peg_order.peg_reference,
            PegReference.BID,
        )
        self.assertEqual(
            peg_order.price,
            Decimal("10"),
        )
        self.assertEqual(peg_order.qty, 150)


    def test_peg_offer_uses_best_offer_price(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("10.5"),
            qty=100,
        )

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("11"),
            qty=200,
        )

        engine.submit_peg(
            reference=PegReference.OFFER,
            side=Side.SELL,
            qty=150,
        )

        peg_order = engine.last_created_order

        self.assertEqual(peg_order.type, OrderType.PEG)
        self.assertEqual(
            peg_order.peg_reference,
            PegReference.OFFER,
        )
        self.assertEqual(
            peg_order.price,
            Decimal("10.5"),
        )
        self.assertEqual(peg_order.qty, 150)


    def test_peg_bid_reprices_and_keeps_priority(self):
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

        engine.submit_peg(
            reference=PegReference.BID,
            side=Side.BUY,
            qty=150,
        )

        peg_order = engine.last_created_order
        peg_id = peg_order.order_id

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10.1"),
            qty=300,
        )

        peg_order = engine.book.find_order(peg_id)

        self.assertIsNotNone(peg_order)
        self.assertEqual(
            peg_order.price,
            Decimal("10.1"),
        )

        orders = engine.book.buy_orders[
            Decimal("10.1")
        ]

        self.assertEqual(
            orders[0].order_id,
            peg_id,
        )

        self.assertEqual(
            orders[0].qty,
            150,
        )

        self.assertEqual(
            orders[1].qty,
            300,
        )


    def test_peg_offer_reprices_when_best_offer_changes(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("10.5"),
            qty=100,
        )

        engine.submit_peg(
            reference=PegReference.OFFER,
            side=Side.SELL,
            qty=150,
        )

        peg_order = engine.last_created_order
        peg_id = peg_order.order_id

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("10.4"),
            qty=200,
        )

        peg_order = engine.book.find_order(peg_id)

        self.assertIsNotNone(peg_order)
        self.assertEqual(
            peg_order.price,
            Decimal("10.4"),
        )


    def test_peg_without_reference_raises_error(self):
        engine = MatchingEngine()

        with self.assertRaisesRegex(
            ValueError,
            "reference price unavailable",
        ):
            engine.submit_peg(
                reference=PegReference.BID,
                side=Side.BUY,
                qty=100,
            )


    def test_pegged_order_is_not_used_as_reference(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=100,
        )

        limit_order = engine.last_created_order

        engine.submit_peg(
            reference=PegReference.BID,
            side=Side.BUY,
            qty=150,
        )

        engine.cancel_order(
            limit_order.order_id
        )

        with self.assertRaisesRegex(
            ValueError,
            "reference price unavailable",
        ):
            engine.submit_peg(
                reference=PegReference.BID,
                side=Side.BUY,
                qty=200,
            )


    def test_peg_reprices_when_reference_is_cancelled(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=100,
        )

        best_limit = engine.last_created_order

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("9"),
            qty=200,
        )

        second_limit = engine.last_created_order

        engine.submit_peg(
            reference=PegReference.BID,
            side=Side.BUY,
            qty=150,
        )

        peg_order = engine.last_created_order
        peg_id = peg_order.order_id

        engine.cancel_order(
            best_limit.order_id
        )

        peg_order = engine.book.find_order(
            peg_id
        )

        self.assertIsNotNone(peg_order)

        self.assertEqual(
            peg_order.price,
            Decimal("9"),
        )

        orders = engine.book.buy_orders[
            Decimal("9")
        ]

        self.assertEqual(
            orders[0].order_id,
            second_limit.order_id,
        )

        self.assertEqual(
            orders[1].order_id,
            peg_id,
        )


    def test_peg_is_suspended_when_reference_disappears(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=100,
        )

        limit_order = engine.last_created_order

        engine.submit_peg(
            reference=PegReference.BID,
            side=Side.BUY,
            qty=150,
        )

        peg_order = engine.last_created_order
        peg_id = peg_order.order_id

        engine.cancel_order(
            limit_order.order_id
        )

        self.assertIsNone(
            engine.book.find_order(peg_id)
        )

        self.assertIsNone(
            engine.book.best_order(Side.BUY)
        )


    def test_suspended_peg_reactivates_when_reference_returns(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=100,
        )

        limit_order = engine.last_created_order

        engine.submit_peg(
            reference=PegReference.BID,
            side=Side.BUY,
            qty=150,
        )

        peg_order = engine.last_created_order
        peg_id = peg_order.order_id

        engine.cancel_order(
            limit_order.order_id
        )

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("9"),
            qty=200,
        )

        new_limit = engine.last_created_order

        peg_order = engine.book.find_order(
            peg_id
        )

        self.assertIsNotNone(peg_order)

        self.assertEqual(
            peg_order.price,
            Decimal("9"),
        )

        orders = engine.book.buy_orders[
            Decimal("9")
        ]

        self.assertEqual(
            orders[0].order_id,
            new_limit.order_id,
        )

        self.assertEqual(
            orders[1].order_id,
            peg_id,
        )


    def test_peg_is_suspended_during_matching_when_reference_is_consumed(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=100,
        )

        engine.submit_peg(
            reference=PegReference.BID,
            side=Side.BUY,
            qty=150,
        )

        peg_order = engine.last_created_order
        peg_id = peg_order.order_id

        trades = engine.submit_limit(
            side=Side.SELL,
            price=Decimal("10"),
            qty=200,
        )

        self.assertEqual(
            len(trades),
            1,
        )

        self.assertEqual(
            trades[0].price,
            Decimal("10"),
        )

        self.assertEqual(
            trades[0].qty,
            100,
        )

        self.assertIsNone(
            engine.book.find_order(peg_id)
        )

        remaining_sell = engine.book.best_order(
            Side.SELL
        )

        self.assertIsNotNone(
            remaining_sell
        )

        self.assertEqual(
            remaining_sell.price,
            Decimal("10"),
        )

        self.assertEqual(
            remaining_sell.qty,
            100,
        )


    def test_market_stops_after_peg_reference_disappears(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=100,
        )

        engine.submit_peg(
            reference=PegReference.BID,
            side=Side.BUY,
            qty=150,
        )

        peg_order = engine.last_created_order
        peg_id = peg_order.order_id

        trades = engine.submit_market(
            side=Side.SELL,
            qty=200,
        )

        self.assertEqual(
            len(trades),
            1,
        )

        self.assertEqual(
            trades[0].qty,
            100,
        )

        self.assertIsNone(
            engine.book.find_order(peg_id)
        )

        self.assertIsNone(
            engine.book.best_order(Side.SELL)
        )


    def test_peg_order_executes_when_reference_price_crosses(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=100,
        )

        trades = engine.submit_peg(
            reference=PegReference.BID,
            side=Side.SELL,
            qty=50,
        )

        self.assertEqual(
            len(trades),
            1,
        )

        self.assertEqual(
            trades[0].price,
            Decimal("10"),
        )

        self.assertEqual(
            trades[0].qty,
            50,
        )
    
    
    def test_market_order_generates_multiple_trades_at_same_price(self):
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
            qty=300,
        )

        self.assertEqual(len(trades), 2)

        self.assertEqual(trades[0].qty, 100)
        self.assertEqual(trades[1].qty, 200)

        self.assertIsNone(
            engine.book.best_order(Side.SELL)
        )


    def test_market_order_crosses_multiple_price_levels_and_respects_priority(self):
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
        self.assertEqual(trades[1].price, Decimal("21"))
        self.assertEqual(trades[2].price, Decimal("22"))

        self.assertEqual(trades[2].qty, 50)


    def test_cancel_non_existing_order_raises_error(self):
        engine = MatchingEngine()

        with self.assertRaises(ValueError):
            engine.cancel_order("ord-999")


    def test_modify_non_existing_order_raises_error(self):
        engine = MatchingEngine()

        self.assertRaises(
            ValueError,
            engine.modify_order,
            "ord-999",
            price=Decimal("10"),
        )       


    def test_cancel_suspended_peg_removes_it_completely(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=100,
        )

        limit_order = engine.last_created_order

        engine.submit_peg(
            reference=PegReference.BID,
            side=Side.BUY,
            qty=50,
        )

        peg_order = engine.last_created_order

        engine.cancel_order(
            limit_order.order_id
        )

        engine.cancel_order(
            peg_order.order_id
        )

        self.assertIsNone(
            engine.pegged_orders.get(peg_order.order_id)
        )


    def test_modify_price_can_change_priority_at_same_price_level(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=100,
        )

        first = engine.last_created_order

        engine.submit_limit(
            side=Side.BUY,
            price=Decimal("10"),
            qty=200,
        )

        second = engine.last_created_order

        engine.modify_order(
            first.order_id,
            price=Decimal("10"),
        )

        orders = engine.book.buy_orders[Decimal("10")]

        self.assertEqual(
            orders[0].order_id,
            first.order_id,
        )
    
    
    def test_peg_offer_sell_follows_best_offer(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("10"),
            qty=100,
        )

        engine.submit_peg(
            reference=PegReference.OFFER,
            side=Side.SELL,
            qty=50,
        )

        peg = engine.last_created_order

        self.assertEqual(
            peg.price,
            Decimal("10"),
        )

        self.assertEqual(
            peg.price,
        Decimal("10"),
        )


    def test_peg_offer_sell_updates_when_best_offer_changes(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("10"),
            qty=100,
        )

        engine.submit_peg(
            reference=PegReference.OFFER,
            side=Side.SELL,
            qty=50,
        )

        peg = engine.last_created_order

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("9"),
            qty=200,
        )

        self.assertEqual(
            peg.price,
            Decimal("9"),
        )


    def test_peg_offer_sell_is_suspended_when_reference_disappears(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("10"),
            qty=100,
        )

        engine.submit_peg(
            reference=PegReference.OFFER,
            side=Side.SELL,
            qty=50,
        )

        peg = engine.last_created_order

        engine.submit_market(
            side=Side.BUY,
            qty=100,
        )

        self.assertIsNone(
            peg.price,
        )

        self.assertNotIn(
            peg.order_id,
            engine.book.orders_by_id,
        )


    def test_peg_offer_sell_reactivates_when_new_offer_exists(self):
        engine = MatchingEngine()

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("10"),
            qty=100,
        )

        engine.submit_peg(
            reference=PegReference.OFFER,
            side=Side.SELL,
            qty=50,
        )

        peg = engine.last_created_order

        engine.submit_market(
            side=Side.BUY,
            qty=100,
        )

        self.assertIsNone(
            peg.price,
        )

        engine.submit_limit(
            side=Side.SELL,
            price=Decimal("12"),
            qty=100,
        )

        self.assertEqual(
            peg.price,
            Decimal("12"),
        )

if __name__ == "__main__":
    unittest.main()