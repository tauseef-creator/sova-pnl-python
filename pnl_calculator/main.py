# pnl_calculator/main.py
import sys
from .config import CHAINS, WALLETS
from .client import get_covalent_client
from .balance.fetcher import fetch_balances
from .transfer.fetcher import fetch_token_transfers
from .pnl.calculator import calculate_token_pnl


def main() -> int:
    client = get_covalent_client()
    results = []

    for chain in CHAINS:
        for wallet in WALLETS:
            print(f"\n{'=' * 60}")
            print(f"WALLET: {wallet} | CHAIN: {chain}")
            print(f"{'=' * 60}")

            try:
                balances_data = fetch_balances(client, wallet, chain)
                assets = balances_data['assets']
                if not assets:
                    print("No assets.")
                    continue

                wallet_pnl = {'wallet': wallet, 'chain': chain, 'pnl': []}

                for token in assets:
                    print(f"\n→ {token['ticker']} | Balance: {token['balance']:.6f}")
                    transfers = fetch_token_transfers(client, chain, wallet, token)
                    print(f"   Transfers: {len(transfers)}")

                    pnl = calculate_token_pnl(token, transfers)
                    wallet_pnl['pnl'].append(pnl)

                    print(
                        f"   Realized: ${pnl['realized_pnl']:,.2f} | "
                        f"Unrealized: ${pnl['unrealized_pnl']:,.2f} | "
                        f"Total: ${pnl['total_pnl']:,.2f}"
                    )

                total = sum(p['total_pnl'] for p in wallet_pnl['pnl'])
                print(f"\nWALLET TOTAL PNL: ${total:,.2f}")
                results.append(wallet_pnl)

            except Exception as e:
                print(f"Error: {e}")

    if results:
        print(f"\n{'=' * 60}")
        print("FINAL SUMMARY")
        print(f"{'=' * 60}")
        for r in results:
            tot = sum(p['total_pnl'] for p in r['pnl'])
            print(f"{r['wallet']} ({r['chain']}): ${tot:,.2f}")

    return 0