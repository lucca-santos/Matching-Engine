import unittest
from decimal import Decimal

from matching_engine import book
from matching_engine.book import OrderBook
from matching_engine.orders import Order, OrderType, Side


class TestOrderBook(unittest.TestCase):

    def test_add_buy_limit_order(self):
        book = OrderBook()

        order = Order(                                        # Criando objeto da classe Order com os parametros passados.   
            side=Side.BUY,                                    # Atributo side do objeto order recebe o valor Side.BUY (enumeração).
            type=OrderType.LIMIT,
            qty=100,
            price=Decimal("10"),
        )

        book.add(order)                                       # Método do objeto book. Adiciona a ordem ao livro de ordens.

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


    def test_format_book_shows_orders_in_price_priority(self):
        book = OrderBook()

        book.add(
            Order(
                side=Side.BUY,
                type=OrderType.LIMIT,
                price=Decimal("9.99"),
                qty=100,
            )
        )

        book.add(
            Order(
                side=Side.BUY,
                type=OrderType.LIMIT,
                price=Decimal("10"),
                qty=200,
            )
        )

        book.add(
         Order(
            side=Side.SELL,
            type=OrderType.LIMIT,
            price=Decimal("10.5"),
            qty=100,
            )
        )

        output = book.format_book()

        self.assertEqual(
            output,
            [
                "Ordens de Compra    | Ordens de Venda",
                "--------------------|--------------------",
                "200 @ 10            | 100 @ 10.5",
                "100 @ 9.99          |",
            ],
        )


    def test_format_book_shows_sell_orders_from_lowest_to_highest_price(self):
        book = OrderBook()

        book.add(
            Order(
                side=Side.SELL,
                type=OrderType.LIMIT,
                price=Decimal("22"),
                qty=100,
            )
        )

        book.add(
            Order(
                side=Side.SELL,
                type=OrderType.LIMIT,
                price=Decimal("20"),
                qty=200,
            )
        )

        book.add(
            Order(
                side=Side.SELL,
                type=OrderType.LIMIT,
                price=Decimal("21"),
                qty=300,
            )
        )

        output = book.format_book()

        self.assertEqual(
            output[2:],
            [
                "                    | 200 @ 20",
                "                    | 300 @ 21",
                "                    | 100 @ 22",
            ],
        )


    def test_format_book_keeps_fifo_at_same_price(self):
        book = OrderBook()

        first_order = Order(
            side=Side.BUY,
            type=OrderType.LIMIT,
            price=Decimal("10"),
            qty=100,
        )

        second_order = Order(
            side=Side.BUY,
            type=OrderType.LIMIT,
            price=Decimal("10"),
            qty=200,
        )

        book.add(first_order)
        book.add(second_order)

        output = book.format_book()

        self.assertEqual(
            output[2:],
            [
                "100 @ 10            |",
                "200 @ 10            |",
            ],
        )
        
    
    def test_find_unknown_order_returns_none(self):
        book = OrderBook()

        self.assertIsNone(
            book.find_order("ord-999")
        )


    def test_remove_order_removes_empty_price_level(self):
        book = OrderBook()

        order = Order(
            side=Side.BUY,
            type=OrderType.LIMIT,
            qty=100,
            price=Decimal("10"),
            order_id="ord-1",
        )

        book.add(order)

        removed = book.remove_order(order)

        self.assertTrue(removed)

        self.assertNotIn(
            Decimal("10"),
            book.buy_orders,
        )


    def test_remove_order_returns_false_when_order_not_in_book(self):
        book = OrderBook()

        order = Order(
            side=Side.BUY,
            type=OrderType.LIMIT,
            qty=100,
            price=Decimal("10"),
            order_id="ord-1",
        )

        self.assertFalse(
            book.remove_order(order)
        )

if __name__ == "__main__":
    unittest.main()