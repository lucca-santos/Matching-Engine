from decimal import Decimal, InvalidOperation

from .engine import MatchingEngine
from .orders import Side


def execute_command(
    engine: MatchingEngine,
    command: str,
) -> list[str]:

    parts = command.strip().split()

    if not parts:
        raise ValueError("comando invalido")

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

        return [str(trade) for trade in trades]

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

        return [str(trade) for trade in trades]

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