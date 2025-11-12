# pnl_calculator/balance/fetcher.py
from typing import List, Dict, Any
from covalent.services.balance_service import BalanceItem

from ..config import QUOTE_CURRENCY, INCLUDE_NFTS, NO_SPAM
from ..utils import format_balance


def fetch_balances(client, wallet: str, chain: str) -> Dict[str, Any]:
    resp = client.balance_service.get_token_balances_for_wallet_address(
        chain_name=chain,
        wallet_address=wallet,
        quote_currency=QUOTE_CURRENCY,
        nft=INCLUDE_NFTS,
        no_spam=NO_SPAM,
    )
    if resp.error:
        raise ValueError(f"Error fetching balances: {resp.error_message}")

    assets: List[Dict[str, Any]] = []
    for item in resp.data.items:
        if item.balance == 0 or item.is_spam:
            continue
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