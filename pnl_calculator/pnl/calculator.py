# pnl_calculator/pnl/calculator.py
from typing import List, Dict, Any

from ..utils import format_balance


def calculate_token_pnl(token: Dict[str, Any], transfers: List[Dict[str, Any]]) -> Dict[str, Any]:
    ticker = token['ticker']
    current_balance = token['balance']
    current_price = token['current_price']
    current_value = token['current_value']

    if current_balance == 0:
        return {
            'ticker': ticker,
            'current_balance': 0.0,
            'current_price': current_price,
            'current_value': 0.0,
            'avg_cost_basis': 0.0,
            'realized_pnl': 0.0,
            'unrealized_pnl': 0.0,
            'total_pnl': 0.0,
            'positions_closed': 0,
        }

    transfers = sorted(transfers, key=lambda x: x['timestamp'])
    buy_queue: List[Dict[str, float]] = []
    realized_pnl = 0.0

    for t in transfers:
        qty = format_balance(t['delta_raw'], t['decimals'])
        usd_value = t['delta_quote'] or 0.0
        gas_usd = t['gas_quote'] or 0.0

        if t['transfer_type'] == 'IN':
            cost_per_unit = (usd_value + gas_usd) / qty if qty > 0 else 0.0
            buy_queue.append({'qty': qty, 'cost_per_unit': cost_per_unit, 'gas_usd': gas_usd})

        elif t['transfer_type'] == 'OUT' and buy_queue:
            sell_qty = abs(qty)
            sell_value_usd = usd_value
            sell_gas_usd = gas_usd
            remaining = sell_qty

            while remaining > 0 and buy_queue:
                pos = buy_queue[0]
                sell_from = min(remaining, pos['qty'])
                entry = sell_from * pos['cost_per_unit']
                exit_val = sell_from * (sell_value_usd / sell_qty)
                pnl_part = exit_val - entry - (sell_gas_usd * (sell_from / sell_qty))

                realized_pnl += pnl_part
                remaining -= sell_from
                pos['qty'] -= sell_from
                if pos['qty'] <= 0:
                    buy_queue.pop(0)

    remaining_qty = sum(p['qty'] for p in buy_queue)
    remaining_cost = sum(p['qty'] * p['cost_per_unit'] for p in buy_queue)
    avg_cost_basis = remaining_cost / remaining_qty if remaining_qty > 0 else 0.0
    unrealized_pnl = (current_price - avg_cost_basis) * current_balance
    total_pnl = realized_pnl + unrealized_pnl
    positions_closed = len([t for t in transfers if t['transfer_type'] == 'OUT'])

    return {
        'ticker': ticker,
        'current_balance': round(current_balance, 6),
        'current_price': round(current_price, 6),
        'current_value': round(current_value, 2),
        'avg_cost_basis': round(avg_cost_basis, 6),
        'realized_pnl': round(realized_pnl, 2),
        'unrealized_pnl': round(unrealized_pnl, 2),
        'total_pnl': round(total_pnl, 2),
        'positions_closed': positions_closed,
    }