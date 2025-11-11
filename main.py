# pnl_calculator.py
import sys
from typing import List, Dict, Any
import pandas as pd
from covalent import CovalentClient
from decimal import Decimal
from covalent.services.balance_service import BalancesResponse, BalanceItem
from covalent.services.util.api_helper import Response

from covalent.services.balance_service import Erc20TransfersResponse, BlockTransactionWithContractTransfers
from datetime import datetime

# -------------------------------------------------
# CONFIG - Edit these
# -------------------------------------------------
API_KEY = "cqt_rQRKdJKWqr888G3hK6bHcHXFGwf3"  # Replace
QUOTE_CURRENCY = "USD"             # Fiat for prices
CHAINS = ["eth-mainnet"]           # List of chains (multi-chain support)
WALLETS = [                        # List for multi-wallet
    "0x00000000219ab540356cBB839Cbe05303d7705Fa"             # Add more
]
INCLUDE_NFTS = False               # Set True for NFTs
NO_SPAM = True                     # Filter spam

# -------------------------------------------------
# Initialize Client (shared)
# -------------------------------------------------
client = CovalentClient(API_KEY)
if not client.balance_service:     # Basic validation
    print("Invalid API key.")
    sys.exit(1)

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def format_balance(balance: int, decimals: int) -> float:
    """Scale raw balance to float."""
    if balance is None or decimals is None:
        return 0.0
    return float(Decimal(balance) / Decimal(10 ** decimals))

def fetch_balances(wallet: str, chain: str) -> Dict:
    """Step 2: Fetch balances (current assets)."""
    resp = client.balance_service.get_token_balances_for_wallet_address(
        chain_name=chain,
        wallet_address=wallet,
        quote_currency=QUOTE_CURRENCY,
        nft=INCLUDE_NFTS,
        no_spam=NO_SPAM,
    )
    if resp.error:
        raise ValueError(f"Error fetching balances: {resp.error_message}")
    
    assets = []
    for item in resp.data.items:
        if item.balance == 0 or item.is_spam: continue  # Skip zero/dust/spam
        assets.append({
            'ticker': item.contract_ticker_symbol,
            'address': item.contract_address,
            'balance': format_balance(item.balance, item.contract_decimals),
            'current_price': item.quote_rate or 0.0,
            'current_value': item.quote or 0.0,
            'type': item.type,
            'native': item.native_token,
        })
    return {
        'wallet': wallet,
        'chain': resp.data.chain_name,
        'updated_at': resp.data.updated_at,
        'assets': assets
    }

def fetch_native_transfers(
    chain: str,
    wallet: str,
    page_size: int = 100
) -> List[Dict[str, Any]]:
    """
    Fetch ALL native token (ETH, BNB, etc.) transfers using paginated v3 endpoint.
    """
    transfers = []
    page = 0

    while True:
        resp = client.transaction_service.get_transactions_for_address_v3(
            chain_name=chain,
            wallet_address=wallet,
            page=page,
            quote_currency=QUOTE_CURRENCY,
            no_logs=True,  # Skip logs to reduce payload
            with_safe=False
        )

        if resp.error:
            print(f"Warning: Native tx page {page} failed: {resp.error_message}")
            break

        data = resp.data

        for tx in data.items:
            if tx.value is None or tx.value <= 0:
                continue

            is_in = tx.to_address and tx.to_address.lower() == wallet.lower()
            transfer_type = "IN" if is_in else "OUT"

            transfers.append({
                'tx_hash': tx.tx_hash,
                'timestamp': tx.block_signed_at,
                'transfer_type': transfer_type,
                'delta_raw': tx.value if is_in else -tx.value,
                'delta_quote': tx.value_quote if is_in else -tx.value_quote,
                'gas_quote': tx.gas_quote or 0.0,
                'decimals': 18
            })

        # Check pagination
        if not data.pagination or not data.pagination.has_more:
            break
        page += 1

    return transfers


def fetch_token_transfers(
    chain: str,
    wallet: str,
    token: Dict[str, Any]
) -> List[Dict[str, Any]]:
    if token.get('native', False):
        return fetch_native_transfers(chain, wallet)
    else:
        # ERC-20: use existing paginated method
        transfers = []
        page_number = 0
        while True:
            resp = client.balance_service.get_erc20_transfers_for_wallet_address_by_page(
                chain_name=chain,
                wallet_address=wallet,
                contract_address=token['address'],
                quote_currency=QUOTE_CURRENCY,
                page_size=1000,
                page_number=page_number
            )
            if resp.error:
                print(f"ERC20 fetch failed: {resp.error_message}")
                break
            data = resp.data
            for tx in data.items:
                if not tx.transfers: continue
                for t in tx.transfers:
                    transfers.append({
                        'tx_hash': t.tx_hash,
                        'timestamp': t.block_signed_at,
                        'transfer_type': t.transfer_type.upper(),
                        'delta_raw': t.delta,
                        'delta_quote': t.delta_quote or 0.0,
                        'gas_quote': tx.gas_quote or 0.0,
                        'decimals': t.contract_decimals
                    })
            if not data.pagination or not data.pagination.has_more:
                break
            page_number += 1
        return transfers


from typing import List, Dict, Any
from decimal import Decimal
from datetime import datetime

def calculate_token_pnl(
    token: Dict[str, Any],
    transfers: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Compute FIFO-based PNL for one token using transfers.
    
    Input:
        token: from fetch_balances → {
            'ticker', 'address', 'balance', 'current_price', 'current_value'
        }
        transfers: list from fetch_token_transfers → [
            {'tx_hash', 'timestamp', 'transfer_type', 'delta_raw', 'delta_quote', 'gas_quote', 'decimals'}
        ]
    
    Output:
        {
            'ticker': str,
            'current_balance': float,
            'current_price': float,
            'current_value': float,
            'avg_cost_basis': float,
            'realized_pnl': float,
            'unrealized_pnl': float,
            'total_pnl': float,
            'positions_closed': int
        }
    """
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
            'positions_closed': 0
        }

    # Sort transfers by timestamp (oldest first) — required for FIFO
    transfers = sorted(transfers, key=lambda x: x['timestamp'])

    # FIFO queue: list of (quantity, cost_per_unit, gas_cost_usd)
    buy_queue: List[Dict[str, float]] = []
    realized_pnl = 0.0
    total_cost = 0.0
    total_qty_bought = 0.0

    for t in transfers:
        qty = format_balance(t['delta_raw'], t['decimals'])
        usd_value = t['delta_quote'] or 0.0
        gas_usd = t['gas_quote'] or 0.0

        if t['transfer_type'] == 'IN':
            # Buy / Receive
            cost_per_unit = (usd_value + gas_usd) / qty if qty > 0 else 0.0
            buy_queue.append({
                'qty': qty,
                'cost_per_unit': cost_per_unit,
                'gas_usd': gas_usd
            })
            total_cost += usd_value + gas_usd
            total_qty_bought += qty

        elif t['transfer_type'] == 'OUT' and buy_queue:
            # Sell / Send
            sell_qty = abs(qty)
            sell_value_usd = usd_value  # Covalent gives exit value
            sell_gas_usd = gas_usd

            remaining_sell = sell_qty
            while remaining_sell > 0 and buy_queue:
                position = buy_queue[0]
                sell_from_this = min(remaining_sell, position['qty'])

                # Realized PNL = (exit_price - entry_price) * qty - gas
                entry_cost = sell_from_this * position['cost_per_unit']
                exit_value = sell_from_this * (sell_value_usd / sell_qty)  # proportional
                pnl_this = exit_value - entry_cost - (sell_gas_usd * (sell_from_this / sell_qty))

                realized_pnl += pnl_this
                remaining_sell -= sell_from_this
                position['qty'] -= sell_from_this

                if position['qty'] <= 0:
                    buy_queue.pop(0)

    # Remaining in queue = current holdings
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
        'positions_closed': positions_closed
    }


# -------------------------------------------------
# Main (Test Step 1 & 2)
# -------------------------------------------------
def main() -> int:
    results = []

    for chain in CHAINS:
        for wallet in WALLETS:
            print(f"\n{'='*60}")
            print(f"WALLET: {wallet} | CHAIN: {chain}")
            print(f"{'='*60}")

            try:
                balances_data = fetch_balances(wallet, chain)
                assets = balances_data['assets']
                if not assets:
                    print("No assets.")
                    continue

                wallet_pnl = {'wallet': wallet, 'chain': chain, 'pnl': []}

                for token in assets:
                    print(f"\n→ {token['ticker']} | Balance: {token['balance']:.6f}")

                    transfers = fetch_token_transfers(
                        chain=chain,
                        wallet=wallet,
                        token=token
                    )
                    print(f"   Transfers: {len(transfers)}")

                    pnl = calculate_token_pnl(token, transfers)
                    wallet_pnl['pnl'].append(pnl)

                    print(f"   Realized: ${pnl['realized_pnl']:,.2f} | "
                          f"Unrealized: ${pnl['unrealized_pnl']:,.2f} | "
                          f"Total: ${pnl['total_pnl']:,.2f}")

                # Aggregate wallet total
                total_pnl = sum(p['total_pnl'] for p in wallet_pnl['pnl'])
                print(f"\nWALLET TOTAL PNL: ${total_pnl:,.2f}")
                results.append(wallet_pnl)

            except Exception as e:
                print(f"Error: {e}")

    # Final summary
    if results:
        print(f"\n{'='*60}")
        print("FINAL SUMMARY")
        print(f"{'='*60}")
        for r in results:
            total = sum(p['total_pnl'] for p in r['pnl'])
            print(f"{r['wallet']} ({r['chain']}): ${total:,.2f}")

    return 0

if __name__ == "__main__":
    sys.exit(main())