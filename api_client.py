"""
API Client wrapper for Covalent API with proper typing.
"""

import time
from typing import List
from covalent import CovalentClient
from covalent.services.balance_service import BalancesResponse, Erc20TransfersResponse
from covalent.services.transaction_service import TransactionsResponse
from covalent.services.util.api_helper import Response

from types import TokenAsset, WalletBalances, TokenTransfer
from utils import format_balance, is_address_equal
from config import Config


class CovalentAPIClient:
    """
    Typed wrapper around Covalent API client.
    
    Provides clean, typed interfaces for fetching blockchain data.
    """
    
    def __init__(self, config: Config):
        """
        Initialize API client.
        
        Args:
            config: Configuration object with API key and settings
        """
        self.config = config
        self.client = CovalentClient(config.api_key)
        
        if not self.client.balance_service:
            raise ValueError("Invalid Covalent API key")
    
    def fetch_balances(self, wallet: str, chain: str) -> WalletBalances:
        """
        Fetch current token balances for a wallet.
        
        Args:
            wallet: Wallet address (0x...)
            chain: Chain name (e.g., 'eth-mainnet')
            
        Returns:
            WalletBalances with current assets
            
        Raises:
            ValueError: If API request fails
        """
        resp: Response[BalancesResponse] = self.client.balance_service.get_token_balances_for_wallet_address(
            chain_name=chain,
            wallet_address=wallet,
            quote_currency=self.config.quote_currency,
            nft=self.config.include_nfts,
            no_spam=self.config.no_spam,
        )
        
        if resp.error:
            raise ValueError(f"Error fetching balances: {resp.error_message}")
        
        assets: List[TokenAsset] = []
        
        for item in resp.data.items:
            # Skip zero balances and spam
            if item.balance == 0 or (item.is_spam and self.config.no_spam):
                continue
            
            assets.append({
                'ticker': item.contract_ticker_symbol or "UNKNOWN",
                'address': item.contract_address or "",
                'balance': format_balance(item.balance, item.contract_decimals),
                'current_price': item.quote_rate or 0.0,
                'current_value': item.quote or 0.0,
                'type': item.type or "cryptocurrency",
                'native': item.native_token or False,
                'decimals': item.contract_decimals or 18,
            })
        
        return {
            'wallet': wallet,
            'chain': resp.data.chain_name,
            'updated_at': resp.data.updated_at,
            'assets': assets,
        }
    
    def fetch_native_transfers(
        self, 
        chain: str, 
        wallet: str, 
        max_pages: int = 1000
    ) -> List[TokenTransfer]:
        """
        Fetch native token transfers (ETH, MATIC, BNB, etc.) for a wallet.
        
        FIXED: Properly checks both from_address and to_address to determine transfer direction.
        
        Args:
            chain: Chain name
            wallet: Wallet address
            max_pages: Maximum number of pages to fetch
            
        Returns:
            List of token transfers
        """
        transfers: List[TokenTransfer] = []
        page_count = 0
        
        if self.config.verbose:
            print(f"[NATIVE] Fetching transfers for {wallet[:10]}... on {chain}")
        
        # Initial page
        resp: Response[TransactionsResponse] = self.client.transaction_service.get_transactions_for_address_v3(
            chain_name=chain,
            wallet_address=wallet,
            page=0,
            quote_currency=self.config.quote_currency,
            no_logs=True,
            with_safe=False
        )
        
        if resp.error:
            if self.config.verbose:
                print(f"[ERROR] Initial page failed: {resp.error_message}")
            return []
        
        data: TransactionsResponse = resp.data
        page_count += 1
        
        while True:
            new_transfers = 0
            
            for tx in data.items:
                # Skip transactions without value
                if tx.value is None or tx.value <= 0:
                    continue
                
                # Skip failed transactions
                if tx.successful is False:
                    continue
                
                # FIXED: Check both from and to addresses
                is_incoming = is_address_equal(tx.to_address, wallet)
                is_outgoing = is_address_equal(tx.from_address, wallet)
                
                # Skip if wallet not involved (shouldn't happen, but safety check)
                if not is_incoming and not is_outgoing:
                    continue
                
                # Determine transfer type and delta
                if is_incoming:
                    transfer_type = "IN"
                    delta_raw = tx.value
                    delta_quote = tx.value_quote or 0.0
                else:  # is_outgoing
                    transfer_type = "OUT"
                    delta_raw = -tx.value
                    delta_quote = -(tx.value_quote or 0.0)
                
                transfers.append({
                    'tx_hash': tx.tx_hash or "",
                    'timestamp': tx.block_signed_at,
                    'transfer_type': transfer_type,
                    'delta_raw': delta_raw,
                    'delta_quote': delta_quote,
                    'gas_quote': tx.gas_quote or 0.0,
                    'decimals': 18,  # Native tokens are always 18 decimals
                    'successful': tx.successful,
                })
                new_transfers += 1
            
            if self.config.verbose:
                print(f"[NATIVE] Page {data.current_page:3d} | Added: {new_transfers:3d} transfers")
            
            # Stop conditions
            if data.links.next is None:
                if self.config.verbose:
                    print(f"[NATIVE] Complete. Total: {len(transfers)} transfers across {page_count} pages")
                break
            
            if page_count >= max_pages:
                if self.config.verbose:
                    print(f"[NATIVE] Reached max_pages ({max_pages})")
                break
            
            # Fetch next page
            next_resp = data.next()
            
            if next_resp.error:
                if next_resp.error_code == 429:
                    print(f"[RATE LIMITED] Waiting {self.config.rate_limit_retry_wait}s...")
                    time.sleep(self.config.rate_limit_retry_wait)
                    continue
                else:
                    if self.config.verbose:
                        print(f"[ERROR] {next_resp.error_message}")
                    break
            
            data = next_resp.data
            page_count += 1
            
            # Rate limiting safety
            if page_count % 10 == 0:
                time.sleep(self.config.rate_limit_pause)
        
        return transfers
    
    def fetch_erc20_transfers(
        self,
        chain: str,
        wallet: str,
        token_address: str
    ) -> List[TokenTransfer]:
        """
        Fetch ERC20 token transfers for a specific token.
        
        Args:
            chain: Chain name
            wallet: Wallet address
            token_address: Token contract address
            
        Returns:
            List of token transfers
        """
        transfers: List[TokenTransfer] = []
        page_number = 0
        
        if self.config.verbose:
            print(f"[ERC20] Fetching transfers for token {token_address[:10]}...")
        
        while True:
            resp: Response[Erc20TransfersResponse] = self.client.balance_service.get_erc20_transfers_for_wallet_address_by_page(
                chain_name=chain,
                wallet_address=wallet,
                contract_address=token_address,
                quote_currency=self.config.quote_currency,
                page_size=1000,
                page_number=page_number
            )
            
            if resp.error:
                if self.config.verbose:
                    print(f"[ERROR] ERC20 fetch failed: {resp.error_message}")
                break
            
            data: Erc20TransfersResponse = resp.data
            page_transfers = 0
            
            for tx in data.items:
                # Skip failed transactions
                if tx.successful is False:
                    continue
                
                if not tx.transfers:
                    continue
                
                for t in tx.transfers:
                    # Determine transfer direction
                    is_incoming = is_address_equal(t.to_address, wallet)
                    transfer_type = "IN" if is_incoming else "OUT"
                    
                    transfers.append({
                        'tx_hash': t.tx_hash or "",
                        'timestamp': t.block_signed_at,
                        'transfer_type': transfer_type,
                        'delta_raw': t.delta,
                        'delta_quote': t.delta_quote or 0.0,
                        'gas_quote': tx.gas_quote or 0.0,
                        'decimals': t.contract_decimals or 18,
                        'successful': tx.successful,
                    })
                    page_transfers += 1
            
            if self.config.verbose:
                print(f"[ERC20] Page {page_number} | Added: {page_transfers} transfers")
            
            if not data.pagination or not data.pagination.has_more:
                break
            
            page_number += 1
        
        if self.config.verbose:
            print(f"[ERC20] Complete. Total: {len(transfers)} transfers")
        
        return transfers
    
    def fetch_token_transfers(
        self,
        chain: str,
        wallet: str,
        token: TokenAsset
    ) -> List[TokenTransfer]:
        """
        Fetch all transfers for a token (native or ERC20).
        
        Args:
            chain: Chain name
            wallet: Wallet address
            token: Token asset info
            
        Returns:
            List of token transfers sorted by timestamp (oldest first)
        """
        if token['native']:
            transfers = self.fetch_native_transfers(chain, wallet, self.config.max_pages)
        else:
            transfers = self.fetch_erc20_transfers(chain, wallet, token['address'])
        
        # Sort by timestamp (oldest first) for FIFO
        return sorted(transfers, key=lambda x: x['timestamp'])
