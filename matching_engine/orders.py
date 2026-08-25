from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional

class Side(str, Enum):                                          # Um Enum serve para representar um conjunto limitado de opções. Deixa o código mais organizado.
    BUY = "buy"
    SELL = "sell"

    @property                                                   # Transforma uma função/método dentro de uma classe em um atributo evita o uso de () para chamar a função.
    def opposite(self) -> "Side":                               # Este método (está dentro de uma classe) garante que vai retornar um objeto do tipo Side. (->): Indica o tipo de retorno da função.
        return Side.SELL if self is Side.BUY else Side.BUY

class OrderType(str, Enum):
    LIMIT = "limit"
    MARKET = "market"

@dataclass
class Order:
    side: Side
    type: OrderType
    qty: int
    price: Optional[Decimal] = None                              # Pode ser decimal ou não existir.