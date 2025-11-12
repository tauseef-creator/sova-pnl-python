# pnl_calculator/transfer/fetcher.py
import time
from typing import List, Dict, Any
from covalent.services.transaction_service import TransactionsResponse
from covalent.services.balance_service import Erc20TransfersResponse

from ..utils import format_balance


# ---------- Native ----------
def _fetch_native(client, chain: str, wallet: str, max_pages: int = 1000) -> List[Dict[str, Any]]:
    transfers = []
    page_count = 0
    print(f"[NATIVE] Starting fetch for {wallet} on {chain}...")

    resp = client.transaction_service.get_transactions_for_address_v3(
        chain_name=chain,
        wallet_address=wallet,
        page=0,
        quote_currency="USD",
        no_logs=True,
        with_safe=False,
    )
    if resp.error:
        print(f"[ERROR] Initial page failed: {resp.error_message}")
        return []

    data: TransactionsResponse = resp.data
    page_count += 1

    while True:
        print(f"[NATIVE] Page {data.current_page:3d} | Items: {len(data.items):3d} | ", end="")
        new = 0
        for tx in data.items:
            if not tx.value or tx.value <= 0:
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
                'decimals': 18,
            })
            new += 1
        print(f"Added: {new:3d}")

        if not data.links.next or page_count >= max_pages:
            break

        next_resp = data.next()
        if next_resp.error:
            if next_resp.error_code == 429:
                print("[RATE LIMITED] Waiting 60s...")
                time.sleep(60)
                continue
            print(f"[ERROR] {next_resp.error_message}")
            break

        data = next_resp.data
        page_count += 1
        if page_count % 10 == 0:
            time.sleep(1)

    print(f"[NATIVE] DONE. Total transfers: {len(transfers)}")
    return transfers


# ---------- ERC-20 ----------
def _fetch_erc20(client, chain: str, wallet: str, contract_address: str) -> List[Dict[str, Any]]:
    transfers = []
    page_number = 0
    while True:
        resp = client.balance_service.get_erc20_transfers_for_wallet_address_by_page(
            chain_name=chain,
            wallet_address=wallet,
            contract_address=contract_address,
            quote_currency="USD",
            page_size=1000,
            page_number=page_number,
        )
        if resp.error:
            print(f"ERC20 fetch failed: {resp.error_message}")
            break

        data: Erc20TransfersResponse = resp.data
        for tx in data.items:
            if not tx.transfers:
                continue
            for t in tx.transfers:
                transfers.append({
                    'tx_hash': t.tx_hash,
                    'timestamp': t.block_signed_at,
                    'transfer_type': t.transfer_type.upper(),
                    'delta_raw': t.delta,
                    'delta_quote': t.delta_quote or 0.0,
                    'gas_quote': tx.gas_quote or 0.0,
                    'decimals': t.contract_decimals,
                })
        if not data.pagination or not data.pagination.has_more:
            break
        page_number += 1
    return transfers


# ---------- Unified ----------
def fetch_token_transfers(client, chain: str, wallet: str, token: Dict[str, Any]) -> List[Dict[str, Any]]:
    if token.get('native', False):
        return _fetch_native(client, chain, wallet)
    else:
        return _fetch_erc20(client, chain, wallet, token['address'])