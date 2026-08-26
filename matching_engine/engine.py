from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from .book import OrderBook
from .orders import Order, OrderType, PegReference, Side


@dataclass
class Trade:
    price: Decimal
    qty: int

    def __str__(self) -> str:                                       # Método criado para formatar o print.
        price = f"{self.price.normalize():f}"

        return f"Trade, price: {price}, qty: {self.qty}"


class MatchingEngine:                                               # Recebe as ordens e decide o que fazer com elas.
                                                                    # Order é o dado, Book é onde as ordens ficam, Engine é quem coordena tudo.
    
    def _validate_qty(self, qty: int) -> None:
        if not isinstance(qty, int) or qty <= 0:
            raise ValueError("qty deve ser um inteiro positivo")
    
    def __init__(self) -> None:                                     # Construtor da classe, inicializa o book e faz com que a classe passe a ter um livro de ofertas.
        self.book = OrderBook()
        
        self.next_order_id = 1
        self.next_sequence = 1
        
        self.last_created_order = None
        
        self.pegged_orders: dict[str, Order] = {}                   # Armazena todas as Pegged Orders existentes, inclusive as que estiverem suspensas.
        self.suspended_peg_ids: set[str] = set()                    # Guarda os IDs das Pegged Orders que perderam temporariamente sua referência.
    
    def _generate_order_id(self) -> str:
        order_id = f"ord-{self.next_order_id}"

        self.next_order_id += 1

        return order_id

    def _generate_sequence(self) -> int:
        sequence = self.next_sequence
        self.next_sequence += 1

        return sequence

    def _reference_price(self, reference: PegReference) -> Optional[Decimal]:     # Busca o preço que uma Pegged Order deve acompanhar.
        if reference is PegReference.BID:
            return self.book.best_limit_price(Side.BUY)                           # Ordens PEG nunca serão referência.

        return self.book.best_limit_price(Side.SELL)

    def _remove_pegged_order(self, order: Order) -> None:                         # Remove definitivamente uma Pegged Order do controle da engine.
        if order.order_id is None:
            return

        self.pegged_orders.pop(order.order_id, None)
        self.suspended_peg_ids.discard(order.order_id)

    def _match_order(self, order: Order, refresh_pegs: bool = True) -> list[Trade]:
        trades = []

        opposite_side = order.side.opposite

        while order.qty > 0:
            best_order = self.book.best_order(opposite_side)

            if best_order is None:
                break

            if order.side is Side.BUY and order.price < best_order.price:
                break

            if order.side is Side.SELL and order.price > best_order.price:
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
                removed_order = self.book.remove_best_order(opposite_side)

                if removed_order is not None and removed_order.type is OrderType.PEG:
                    self._remove_pegged_order(removed_order)

                if refresh_pegs:
                    trades.extend(self._refresh_pegged_orders())

        return trades

    def _refresh_pegged_orders(self) -> list[Trade]:                              # Atualiza as Pegged Orders quando o preço de referência muda.
        trades = []

        changed = True

        while changed:
            changed = False

            for order in list(self.pegged_orders.values()):     # noqa: S7504     # Crio uma cópia das Pegged Orders antes de iterar porque algumas delas podem ser removidas (pop) do dicionário durante a atualização.
                if order.qty <= 0:
                    self._remove_pegged_order(order)
                    changed = True
                    continue

                reference_price = self._reference_price(order.peg_reference)

                active = (
                    order.order_id is not None
                    and self.book.find_order(order.order_id) is order
                )

                if reference_price is None:
                    if active:
                        self.book.remove_order(order)
                        order.price = None
                        self.suspended_peg_ids.add(order.order_id)
                        changed = True

                    continue

                if active and order.price == reference_price:
                    continue

                if active:
                    self.book.remove_order(order)
                    order.price = reference_price

                else:
                    order.price = reference_price
                    order.sequence = self._generate_sequence()
                    self.suspended_peg_ids.discard(order.order_id)

                peg_trades = self._match_order(order, refresh_pegs=False)
                trades.extend(peg_trades)

                if order.qty > 0:
                    self.book.add(order)
                else:
                    self._remove_pegged_order(order)

                changed = True

        return trades

    def submit_limit(
        self,
        side: Side,
        price: Decimal,
        qty: int,
        order_id: Optional[str] = None,
    ) -> list[Trade]:
        
        self.last_created_order = None
        
        self._validate_qty(qty)

        if order_id is None:
            order_id = self._generate_order_id()
        
        order = Order(
            side=side,
            type=OrderType.LIMIT,
            qty=qty,
            price=price,
            order_id=order_id,
            sequence=self._generate_sequence(),
        )   

        trades = self._match_order(order)

        if order.qty > 0:
            self.book.add(order)
            
            trades.extend(self._refresh_pegged_orders())
            
            if self.book.find_order(order_id) is order:
                self.last_created_order = order

        else:
            trades.extend(self._refresh_pegged_orders())

        return trades

    def submit_market(                                             # Método para enviar uma ordem market para a matching engine e aí, ela mesmo vai decidir o que fazer com essa ordem.
        self,
        side: Side,
        qty: int,
    ) -> list[Trade]:                                              # Uma única Market Order pode gerar várias Trades, então o retorno é uma lista de Trades.
        
        self._validate_qty(qty)

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
                removed_order = self.book.remove_best_order(opposite_side)
                
                if removed_order is not None and removed_order.type is OrderType.PEG:
                    self._remove_pegged_order(removed_order)

                trades.extend(self._refresh_pegged_orders())

        return trades
    
    def submit_peg(
        self,
        reference: PegReference,
        side: Side,
        qty: int,
    ) -> list[Trade]:

        self.last_created_order = None
        
        self._validate_qty(qty)

        reference_price = self._reference_price(reference)

        if reference_price is None:
            raise ValueError("reference price unavailable")

        order_id = self._generate_order_id()

        order = Order(
            side=side,
            type=OrderType.PEG,
            qty=qty,
            price=reference_price,
            order_id=order_id,
            peg_reference=reference,
            sequence=self._generate_sequence(),
        )

        self.pegged_orders[order_id] = order

        trades = []

        while True:
            current_reference = self._reference_price(reference)

            if current_reference is None:
                order.price = None
                self.suspended_peg_ids.add(order_id)
                trades.extend(self._refresh_pegged_orders())
                return trades

            order.price = current_reference

            trades.extend(
                self._match_order(
                    order,
                    refresh_pegs=False,
                )
            )

            if order.qty == 0:
                self._remove_pegged_order(order)
                trades.extend(self._refresh_pegged_orders())
                return trades

            if self._reference_price(reference) == current_reference:
                break

        self.book.add(order)

        trades.extend(self._refresh_pegged_orders())

        if self.book.find_order(order_id) is order:
            self.last_created_order = order

        return trades
    
    def cancel_order(self, order_id: str) -> list[Trade]:
        order = self.book.find_order(order_id)
        
        if order is not None:
            self.book.remove_order(order)

            if order.type is OrderType.PEG:
                self._remove_pegged_order(order)

            return self._refresh_pegged_orders()                                           # A ordem cancelada pode ter sido a referência de alguma Pegged Order, então é necessário atualizar as Pegged Orders para ver se alguma delas precisa ser suspensa ou reprecificada.

        suspended_order = self.pegged_orders.get(order_id)

        if suspended_order is not None and order_id in self.suspended_peg_ids:
            self._remove_pegged_order(suspended_order)
            return []

        raise ValueError("ordem nao encontrada")
    
    def modify_order(
        self,
        order_id: str,
        price: Optional[Decimal] = None,
        qty: Optional[int] = None,
    ) -> list[Trade]:

        order = self.book.find_order(order_id)

        if order is None:
            raise ValueError("ordem nao encontrada")
        
        if order.type is OrderType.PEG:

            if price is not None:
                raise ValueError("ordem pegged nao permite alteracao manual de preco")

            if qty is not None:
                self._validate_qty(qty)

                order.qty = qty

            return []

        new_price = order.price if price is None else price
        new_qty = order.qty if qty is None else qty
        
        self._validate_qty(new_qty)

        price_changed = new_price != order.price
        quantity_increased = new_qty > order.qty

        if not price_changed and not quantity_increased:
            order.qty = new_qty
            return []

        side = order.side

        self.book.remove_order(order)
        
        if order.type is OrderType.PEG:
            self._remove_pegged_order(order)

        return self.submit_limit(
            side=side,
            price=new_price,
            qty=new_qty,
            order_id=order_id,
        )