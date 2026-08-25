from __future__ import annotations

from collections import deque
from decimal import Decimal
from typing import Deque, Dict, Optional

from .orders import Order, OrderType, Side


class OrderBook:
    def __init__(self) -> None:                                                   # Inicializa o livro de ordens com dicionários para ordens de compra e venda, onde as chaves são preços (Decimal) e os valores são filas (deque) de ordens (Order).
        self.buy_orders: Dict[Decimal, Deque[Order]] = {}      
        self.sell_orders: Dict[Decimal, Deque[Order]] = {}

    def _get_side_book(self, side: Side) -> Dict[Decimal, Deque[Order]]:          # O self representa a instância/objeto da classe, e é usado para acessar variáveis que pertencem à classe.
        if side is Side.BUY:
            return self.buy_orders

        return self.sell_orders

    def add(self, order: Order) -> None:                                           # Adiciona uma ordem ao livro de ordens, verificando se é uma ordem limit e se o preço é válido, e adicionando a ordem à fila correspondente no dicionário do lado correto (compra ou venda).
        if order.type is not OrderType.LIMIT:
            raise ValueError("somente ordens limit podem permanecer no livro")

        if order.price is None or order.price <= 0:
            raise ValueError("ordem limit precisa possuir preco maior que zero")

        side_book = self._get_side_book(order.side)                                # Descobrindo o lado da ordem e armazenando o dicionário correspondente (buy_orders ou sell_orders) na variável side_book.

        if order.price not in side_book:                                           # Verifica se tem uma fila para o preço da ordem. Se não tiver, cria uma nova fila para esse preço.
            side_book[order.price] = deque()

        side_book[order.price].append(order)

    def best_price(self, side: Side) -> Optional[Decimal]:                         # Diz o melhor preço para o lado da ordem.
        side_book = self._get_side_book(side)

        if not side_book:                                                          # Verifica se o dicionário side_book está vazio.
            return None

        if side is Side.BUY:                                
            return max(side_book)                                                  # O melhor preço de compra é o maior preço disponível (BID).

        return min(side_book)                                                      # O melhor preço de venda é o menor preço disponível (ASK/OFFER).

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

        if not orders_at_price:                                                  # Verifica se a fila de ordens para o melhor preço do lado X está vazia. Se estiver, remove a chave (preço) do dicionário side_book.
            del side_book[price]

        return order                                                             # Devolve a ordem que saiu.