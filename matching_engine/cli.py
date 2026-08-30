from decimal import Decimal, InvalidOperation

from .engine import MatchingEngine, Trade
from .orders import Side, PegReference


def aggregate_trades(trades: list[Trade]) -> list[Trade]:
    aggregated = []

    for trade in trades:
        if aggregated and aggregated[-1].price == trade.price:
            aggregated[-1].qty += trade.qty
        else:
            aggregated.append(
                Trade(
                    price=trade.price,
                    qty=trade.qty,
                )
            )

    return aggregated

def execute_command(
    engine: MatchingEngine,
    command: str,
) -> list[str]:

    parts = command.strip().split()

    if not parts:
        raise ValueError("comando invalido")

    # Limit
    if parts[0] == "limit":
        if len(parts) != 4:
            raise ValueError("comando limit invalido")

        try:
            side = Side(parts[1])
            price = Decimal(parts[2])
            qty = int(parts[3])
        except (ValueError, InvalidOperation):
            raise ValueError("comando limit invalido") from None

        trades = engine.submit_limit(
            side=side,
            price=price,
            qty=qty,
        )

        output = [
            str(trade)
            for trade in aggregate_trades(trades)
        ]

        created_order = engine.last_created_order

        if created_order is not None:
            price = f"{created_order.price.normalize():f}"

            output.append(
                f"Order created: "
                f"{created_order.side.value} "
                f"{created_order.qty} @ {price} "
                f"{created_order.order_id}"
            )

        return output

    # Mercado
    if parts[0] == "market":
        if len(parts) != 3:
            raise ValueError("comando market invalido")

        try:
            side = Side(parts[1])
            qty = int(parts[2])
        except ValueError:
            raise ValueError("comando market invalido") from None

        trades = engine.submit_market(
            side=side,
            qty=qty,
        )

        return [
            str(trade)
            for trade in aggregate_trades(trades)
        ]

    # Print book
    if parts[0] == "print" and len(parts) == 2 and parts[1] == "book":
        return engine.book.format_book()

    # Cancela ordem
    if parts[0] == "cancel":
        if len(parts) != 3 or parts[1] != "order":
            raise ValueError("comando cancel invalido")

        engine.cancel_order(parts[2])
        
        return ["Order cancelled"]
    
    # Modifica ordem
    if parts[0] == "modify":
        if len(parts) not in (5, 7) or parts[1] != "order":
            raise ValueError("comando modify invalido")

        order_id = parts[2]

        price = None
        qty = None
        reference = None

        changes = parts[3:]

        try:
            for index in range(0, len(changes), 2):
                field = changes[index]
                value = changes[index + 1]

                if field == "price":
                    price = Decimal(value)
                    
                elif field == "reference":
                    reference = PegReference(value)

                elif field == "qty":
                    qty = int(value)

                else:
                    raise ValueError

        except (ValueError, InvalidOperation):
            raise ValueError("comando modify invalido") from None

        trades = engine.modify_order(
            order_id=order_id,
            price=price,
            qty=qty,
            reference=reference,
        )

        output = [
            str(trade)
            for trade in aggregate_trades(trades)
        ]

        output.append("Order modified")

        return output
    
    # Pegged
    if parts[0] == "peg":
        if len(parts) != 4:
            raise ValueError("comando peg invalido")

        try:
            reference = PegReference(parts[1])
            side = Side(parts[2])
            qty = int(parts[3])

        except ValueError:
            raise ValueError("comando peg invalido") from None

        trades = engine.submit_peg(
            reference=reference,
            side=side,
            qty=qty,
        )

        output = [
            str(trade)
            for trade in aggregate_trades(trades)
        ]

        created_order = engine.last_created_order

        if created_order is not None:
            price = f"{created_order.price.normalize():f}"

            output.append(
                f"Order created: "
                f"{created_order.side.value} "
                f"{created_order.qty} @ {price} "
                f"{created_order.order_id}"
            )

        return output

    raise ValueError("comando invalido")


def main() -> None:
    engine = MatchingEngine()

    while True:
        try:
            command = input(">>> ").strip()

            if command in ("exit", "quit"):
                break

            output = execute_command(
                engine,
                command,
            )

            for line in output:
                print(line)

        except ValueError as error:
            print(f"Error: {error}")
            
        except (EOFError, KeyboardInterrupt):
            break