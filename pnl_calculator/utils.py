# pnl_calculator/utils.py
from decimal import Decimal


def format_balance(balance: int, decimals: int) -> float:
    """Scale raw balance to float."""
    if balance is None or decimals is None:
        return 0.0
    return float(Decimal(balance) / Decimal(10 ** decimals))