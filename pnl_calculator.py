"""
Main PNL Calculator - Production-ready blockchain wallet PNL calculator.

This module orchestrates the entire PNL calculation workflow with:
- Typed API interactions
- Comprehensive error handling
- Price validation
- Balance reconciliation  
- Detailed reporting

Usage:
    from pnl_calculator import WalletPNLCalculator
    from config import Config
    
    config = Config(
        api_key="cqt_...",
        wallets=["0x..."],
        chains=["eth-mainnet"]
    )
    
    calculator = WalletPNLCalculator(config)
    results = calculator.calculate_all()
"""

from typing import List
from pnl_types import WalletPNL, TokenPNL
from config import Config
from api_client import CovalentAPIClient
from pnl_engine import PNLCalculator
from utils import (
    format_currency,
    format_percentage,
    truncate_address,
    format_timestamp
)


class WalletPNLCalculator:
    """
    High-level orchestrator for wallet PNL calculations.
    """
    
    def __init__(self, config: Config):
        """
        Initialize calculator with configuration.
        
        Args:
            config: Configuration object with API key and settings
        """
        self.config = config
        self.api_client = CovalentAPIClient(config)
        self.pnl_engine = PNLCalculator(config)
    
    def calculate_wallet_pnl(self, wallet: str, chain: str) -> WalletPNL:
        """
        Calculate PNL for a single wallet on a single chain.
        
        Args:
            wallet: Wallet address
            chain: Chain name (e.g., 'eth-mainnet')
            
        Returns:
            WalletPNL with aggregated results
            
        Raises:
            ValueError: If API requests fail
        """
        if self.config.verbose:
            print(f"\n{'='*70}")
            print(f"WALLET: {truncate_address(wallet)} | CHAIN: {chain}")
            print(f"{'='*70}")
        
        # Fetch current balances
        balances_data = self.api_client.fetch_balances(wallet, chain)
        assets = balances_data['assets']
        
        if not assets:
            if self.config.verbose:
                print("No assets found in wallet.")
            return self._create_empty_wallet_pnl(wallet, chain)
        
        if self.config.verbose:
            print(f"\nFound {len(assets)} tokens with non-zero balances")
            print(f"Updated at: {format_timestamp(balances_data['updated_at'])}\n")
        
        # Calculate PNL for each token
        token_pnls: List[TokenPNL] = []
        
        for token in assets:
            if self.config.verbose:
                print(f"→ {token['ticker']:8s} | Balance: {token['balance']:12.6f} | "
                      f"Price: {format_currency(token['current_price'])}")
            
            try:
                # Fetch transfer history
                transfers = self.api_client.fetch_token_transfers(chain, wallet, token)
                
                if self.config.verbose:
                    print(f"  Fetched {len(transfers)} transfers")
                
                # Calculate PNL
                pnl = self.pnl_engine.calculate_token_pnl(token, transfers)
                token_pnls.append(pnl)
                
                # Display results
                self._display_token_pnl(pnl)
                
            except Exception as e:
                print(f"  ❌ Error calculating PNL: {e}")
                if self.config.verbose:
                    import traceback
                    traceback.print_exc()
        
        # Aggregate wallet-level PNL
        return self._aggregate_wallet_pnl(wallet, chain, token_pnls)
    
    def calculate_all(self) -> List[WalletPNL]:
        """
        Calculate PNL for all configured wallets across all chains.
        
        Returns:
            List of WalletPNL results
        """
        results: List[WalletPNL] = []
        
        print("\n" + "="*70)
        print("BLOCKCHAIN WALLET PNL CALCULATOR")
        print("="*70)
        print(f"Chains: {', '.join(self.config.chains)}")
        print(f"Wallets: {len(self.config.wallets)}")
        print(f"Quote Currency: {self.config.quote_currency}")
        print("="*70)
        
        for chain in self.config.chains:
            for wallet in self.config.wallets:
                try:
                    wallet_pnl = self.calculate_wallet_pnl(wallet, chain)
                    results.append(wallet_pnl)
                    
                except Exception as e:
                    print(f"\n❌ Error processing {truncate_address(wallet)} on {chain}: {e}")
                    if self.config.verbose:
                        import traceback
                        traceback.print_exc()
        
        # Display final summary
        self._display_summary(results)
        
        return results
    
    def _aggregate_wallet_pnl(
        self,
        wallet: str,
        chain: str,
        token_pnls: List[TokenPNL]
    ) -> WalletPNL:
        """Aggregate token-level PNL into wallet-level totals."""
        total_invested = sum(p['total_invested'] for p in token_pnls)
        total_current_value = sum(p['current_value'] for p in token_pnls)
        total_realized_pnl = sum(p['realized_pnl'] for p in token_pnls)
        total_unrealized_pnl = sum(p['unrealized_pnl'] for p in token_pnls)
        total_pnl = total_realized_pnl + total_unrealized_pnl
        
        if total_invested > 0:
            total_roi_percent = (
                (total_current_value + total_realized_pnl - total_invested) / 
                total_invested * 100
            )
        else:
            total_roi_percent = 0.0
        
        return {
            'wallet': wallet,
            'chain': chain,
            'tokens': token_pnls,
            'total_invested': round(total_invested, 2),
            'total_current_value': round(total_current_value, 2),
            'total_realized_pnl': round(total_realized_pnl, 2),
            'total_unrealized_pnl': round(total_unrealized_pnl, 2),
            'total_pnl': round(total_pnl, 2),
            'total_roi_percent': round(total_roi_percent, 2),
        }
    
    def _create_empty_wallet_pnl(self, wallet: str, chain: str) -> WalletPNL:
        """Create empty wallet PNL for wallets with no assets."""
        return {
            'wallet': wallet,
            'chain': chain,
            'tokens': [],
            'total_invested': 0.0,
            'total_current_value': 0.0,
            'total_realized_pnl': 0.0,
            'total_unrealized_pnl': 0.0,
            'total_pnl': 0.0,
            'total_roi_percent': 0.0,
        }
    
    def _display_token_pnl(self, pnl: TokenPNL) -> None:
        """Display token PNL in console."""
        if not self.config.verbose:
            return
        
        print(f"  ├─ Cost Basis: {format_currency(pnl['avg_cost_basis'])}")
        print(f"  ├─ Invested:   {format_currency(pnl['total_invested'])}")
        print(f"  ├─ Value Now:  {format_currency(pnl['current_value'])}")
        print(f"  ├─ Realized:   {format_currency(pnl['realized_pnl'])}")
        print(f"  ├─ Unrealized: {format_currency(pnl['unrealized_pnl'])}")
        print(f"  ├─ Total PNL:  {format_currency(pnl['total_pnl'])} "
              f"({format_percentage(pnl['roi_percent'])})")
        print(f"  └─ Positions:  {pnl['positions_opened']} opened, "
              f"{pnl['positions_closed']} closed")
        
        # Display warnings
        if pnl['has_warnings']:
            print("  ⚠️  WARNINGS:")
            for warning in pnl['warnings']:
                print(f"     • {warning}")
        
        print()
    
    def _display_summary(self, results: List[WalletPNL]) -> None:
        """Display final summary of all results."""
        if not results:
            print("\nNo results to display.")
            return
        
        print("\n" + "="*70)
        print("FINAL SUMMARY")
        print("="*70)
        
        for wallet_pnl in results:
            wallet_short = truncate_address(wallet_pnl['wallet'])
            chain = wallet_pnl['chain']
            total_pnl = wallet_pnl['total_pnl']
            roi = wallet_pnl['total_roi_percent']
            
            print(f"{wallet_short:14s} | {chain:18s} | "
                  f"PNL: {format_currency(total_pnl):15s} | "
                  f"ROI: {format_percentage(roi):10s}")
            
            if self.config.verbose and wallet_pnl['tokens']:
                print(f"  Tokens analyzed: {len(wallet_pnl['tokens'])}")
                tokens_with_warnings = sum(1 for t in wallet_pnl['tokens'] if t['has_warnings'])
                if tokens_with_warnings > 0:
                    print(f"  ⚠️  Tokens with warnings: {tokens_with_warnings}")
        
        # Grand total across all wallets
        if len(results) > 1:
            grand_total = sum(r['total_pnl'] for r in results)
            print(f"\n{'─'*70}")
            print(f"GRAND TOTAL PNL: {format_currency(grand_total)}")
        
        print("="*70 + "\n")
