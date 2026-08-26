from __future__ import annotations

from collections import deque
from decimal import Decimal
from typing import Deque, Dict, Optional

from .orders import Order, OrderType, Side


class OrderBook:
    def __init__(self) -> None:                                                   # Inicializa o livro de ordens com dicionários para ordens de compra e venda, onde as chaves são preços (Decimal) e os valores são filas (deque) de ordens (Order).
        self.buy_orders: Dict[Decimal, Deque[Order]] = {}      
        self.sell_orders: Dict[Decimal, Deque[Order]] = {}
        
        self.orders_by_id: Dict[str, Order] = {}

    def _get_side_book(self, side: Side) -> Dict[Decimal, Deque[Order]]:          # O self representa a instância/objeto da classe, e é usado para acessar variáveis que pertencem à classe.
        if side is Side.BUY:
            return self.buy_orders

        return self.sell_orders

    def add(self, order: Order) -> None:                                           # Adiciona uma ordem ao livro de ordens, verificando se é uma ordem limit e se o preço é válido, e adicionando a ordem à fila correspondente no dicionário do lado correto (compra ou venda).
        if order.type not in (OrderType.LIMIT, OrderType.PEG):
            raise ValueError("somente ordens limit e peg podem permanecer no livro")

        if order.price is None or order.price <= 0:
            raise ValueError("ordem precisa possuir preco maior que zero")

        side_book = self._get_side_book(order.side)                                # Descobrindo o lado da ordem e armazenando o dicionário correspondente (buy_orders ou sell_orders) na variável side_book.

        if order.price not in side_book:                                           # Verifica se tem uma fila para o preço da ordem. Se não tiver, cria uma nova fila para esse preço.
            side_book[order.price] = deque()

        orders_at_price = side_book[order.price]                                   # Pega a fila de ordens que já estão nesse mesmo preço.

        if not orders_at_price or orders_at_price[-1].sequence <= order.sequence:
            orders_at_price.append(order)

        else:
            for index, existing_order in enumerate(orders_at_price):
                if existing_order.sequence > 0 and existing_order.sequence > order.sequence:
                    orders_at_price.insert(index, order)
                    break                                          # Se não encontrou uma posição anterior, adiciona a ordem ao final da fila.

        if order.order_id is not None:
            self.orders_by_id[order.order_id] = order

    def best_price(self, side: Side) -> Optional[Decimal]:                         # Diz o melhor preço para o lado da ordem.
        side_book = self._get_side_book(side)

        if not side_book:                                                          # Verifica se o dicionário side_book está vazio.
            return None

        if side is Side.BUY:                                
            return max(side_book)                                                  # O melhor preço de compra é o maior preço disponível (BID).

        return min(side_book)                                                      # O melhor preço de venda é o menor preço disponível (ASK/OFFER).

    def best_limit_price(self, side: Side) -> Optional[Decimal]:                  # Retorna o melhor preço de referência considerando somente ordens LIMIT, para facilitar a lógica de PEG.
        side_book = self._get_side_book(side)

        valid_prices = []

        for price, orders in side_book.items():
            for order in orders:
                if order.type is OrderType.LIMIT:
                    valid_prices.append(price)
                    break

        if not valid_prices:
            return None

        if side is Side.BUY:
            return max(valid_prices)

        return min(valid_prices)

    def best_order(self, side: Side) -> Optional[Order]:                           # Diz qual ordem deve ser executada primeiro para um lado X no melhor preço.
        price = self.best_price(side)                                              # Atribui o melhor preço para o lado correspondente.

        if price is None:
            return None

        side_book = self._get_side_book(side)

        return side_book[price][0]                                                # Pega o primeiro elemento da fila de ordens para o melhor preço do lado X.

    def remove_best_order(self, side: Side) -> Optional[Order]:
        price = self.best_price(side)

        if price is None:
            return None

        side_book = self._get_side_book(side)
        orders_at_price = side_book[price]                                       # Pega a fila de ordens para o melhor preço do lado X.

        order = orders_at_price.popleft()                                        # Remove o primeiro elemento da fila de ordens para o melhor preço do lado X.
        
        if order.order_id is not None:                                           # Se uma ordem foi totalmente executada, ela também precisa sair do dicionário de ordens por ID, para que não seja possível cancelar uma ordem que já foi executada.
            self.orders_by_id.pop(order.order_id, None)

        if not orders_at_price:                                                  # Verifica se a fila de ordens para o melhor preço do lado X está vazia. Se estiver, remove a chave (preço) do dicionário side_book.
            del side_book[price]

        return order                                                             # Devolve a ordem que saiu.

    def format_book(self) -> list[str]:
        buy_rows = []
        sell_rows = []

        for price in sorted(self.buy_orders, reverse=True):
            for order in self.buy_orders[price]:
                buy_rows.append(
                    f"{order.qty} @ {order.price}"
                )

        for price in sorted(self.sell_orders):
            for order in self.sell_orders[price]:
                sell_rows.append(
                    f"{order.qty} @ {order.price}"
                )

        lines = [
            "Ordens de Compra    | Ordens de Venda",
            "--------------------|--------------------",
        ]

        total_rows = max(
            len(buy_rows),
            len(sell_rows),
        )

        for index in range(total_rows):
            buy = buy_rows[index] if index < len(buy_rows) else ""
            sell = sell_rows[index] if index < len(sell_rows) else ""

            if sell:
                lines.append(
                    f"{buy:<20}| {sell}"
                )
            else:
                lines.append(
                    f"{buy:<20}|"
                )

        return lines
    
    def find_order(self, order_id: str) -> Optional[Order]:
        return self.orders_by_id.get(order_id)


    def remove_order(self, order: Order) -> bool:
        if order.price is None:
            return False

        side_book = self._get_side_book(order.side)

        if order.price not in side_book:
            return False

        orders_at_price = side_book[order.price]

        try:
            orders_at_price.remove(order)
        except ValueError:
            return False

        if not orders_at_price:
            del side_book[order.price]

        if order.order_id is not None:
            self.orders_by_id.pop(order.order_id, None)

        return True