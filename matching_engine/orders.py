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

class OrderType(str, Enum):                                     # Cada valor desse Enum se comporta como uma string, mas também é um objeto do tipo OrderType. Isso permite que você use os valores do Enum como strings, mas também aproveite os benefícios de ter um tipo específico para representar os tipos de ordens.
    LIMIT = "limit"
    MARKET = "market"
    PEG = "peg"
    
class PegReference(str, Enum):                                 # Define qual preço a ordem peg vai seguir.
    BID = "bid"
    OFFER = "offer"

@dataclass
class Order:
    side: Side
    type: OrderType
    qty: int
    price: Optional[Decimal] = None                              # Pode ser decimal ou não existir.
    order_id: Optional[str] = None                               # identifica a ordem.
    peg_reference: Optional[PegReference] = None                 # BID ou OFFER, caso seja uma ordem PEG.
    sequence: int = 0                                            # Identifica a prioridade temporal da ordem.