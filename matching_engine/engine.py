from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .book import OrderBook
from .orders import Order, OrderType, Side


@dataclass
class Trade:
    price: Decimal
    qty: int

    def __str__(self) -> str:                                       # Método criado para formatar o print.
        price = f"{self.price.normalize():f}"

        return f"Trade, price: {price}, qty: {self.qty}"


class MatchingEngine:                                               # Recebe as ordens e decide o que fazer com elas.
                                                                    # Order é o dado, Book é onde as ordens ficam, Engine é quem coordena tudo.
    def __init__(self) -> None:                                     # Construtor da classe, inicializa o book e faz com que a classe passe a ter um livro de ofertas.
        self.book = OrderBook()

    def submit_limit(
        self,
        side: Side,
        price: Decimal,
        qty: int,
    ) -> list[Trade]:

        order = Order(
            side=side,
            type=OrderType.LIMIT,
            qty=qty,
            price=price,
        )   

        trades = []

        opposite_side = side.opposite

        while order.qty > 0:
            best_order = self.book.best_order(opposite_side)

            if best_order is None:
                break

            if side is Side.BUY and price < best_order.price:
                break

            if side is Side.SELL and price > best_order.price:
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

        if order.qty > 0:
            self.book.add(order)

        return trades

    def submit_market(                                             # Método para enviar uma ordem market para a matching engine e aí, ela mesmo vai decidir o que fazer com essa ordem.
        self,
        side: Side,
        qty: int,
    ) -> list[Trade]:                                              # Uma única Market Order pode gerar várias Trades, então o retorno é uma lista de Trades.

        order = Order(                                             # Matching engine cria o objeto order com os parâmetros recebidos.
            side=side,
            type=OrderType.MARKET,
            qty=qty,
        )

        opposite_side = side.opposite                              # Descobrindo qual lado precisa consultar. BUY consulta SELL.
        trades = []                                                # Lista vazia para armazenar as trades que vão ser geradas a partir da execução da ordem market.

        while order.qty > 0:                                       # Enquanto a quantidade da ordem market for maior que zero, vai continuar consumindo o book.

            best_order = self.book.best_order(opposite_side)       # Verifica a melhor ordem do lado oposto.

            if best_order is None:
                break

            trade_qty = min(                                       # Pego o mínimo entre a quantidade da ordem market e a quantidade da melhor ordem do lado oposto, para não executar mais do que está disponível no book.
                order.qty,
                best_order.qty,
            )

            trade = Trade(                                         # Cria um objeto Trade com os parâmetros da negociação. Representao negócio realizdo.
                price=best_order.price,
                qty=trade_qty,
            )

            trades.append(trade)                                   # Adiciona a trade executaod na lista de trades.

            order.qty -= trade_qty                                 # Subtrai da ordem market a quantidade que acabou de ser executada. Se ainda restar quantidade, a ordem market continuará consumindo as ordens do lado oposto.
            best_order.qty -= trade_qty                            # Atualiza a quantidade restante da melhor ordem do book após o trade.

            if best_order.qty == 0:                                # Se a best order foi executada completamente, remove ela do livro de ofertas.
                self.book.remove_best_order(opposite_side)

        return trades