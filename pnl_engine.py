"""
Core PNL Calculation Engine with comprehensive validation and error handling.
"""

from typing import List
from types import TokenAsset, TokenTransfer, TokenPNL, FIFOPosition
from utils import (
    format_balance,
    calculate_roi,
    is_approximately_equal,
    safe_divide
)
from config import Config


class PNLCalculator:
    """
    FIFO-based PNL calculator with price validation and balance reconciliation.
    """
    
    def __init__(self, config: Config):
        """
        Initialize PNL calculator.
        
        Args:
            config: Configuration object
        """
        self.config = config
    
    def calculate_token_pnl(
        self,
        token: TokenAsset,
        transfers: List[TokenTransfer]
    ) -> TokenPNL:
        """
        Calculate comprehensive PNL for a single token using FIFO method.
        
        Features:
        - FIFO cost basis tracking
        - Gas fee accounting
        - Price validation with warnings
        - Balance reconciliation
        - Handles sold-out positions
        
        Args:
            token: Token asset information
            transfers: List of all transfers for this token (sorted by timestamp)
            
        Returns:
            TokenPNL with detailed profit/loss breakdown
        """
        ticker = token['ticker']
        current_balance = token['balance']
        current_price = token['current_price']
        current_value = token['current_value']
        
        warnings: List[str] = []
        
        # Handle tokens with no transfers (airdrops, initial holdings)
        if not transfers:
            if current_balance > 0:
                warnings.append(f"No transfer history found but balance exists ({current_balance:.6f})")
                return self._create_pnl_result(
                    token=token,
                    avg_cost_basis=0.0,
                    total_invested=0.0,
                    realized_pnl=0.0,
                    unrealized_pnl=current_value,
                    positions_opened=0,
                    positions_closed=0,
                    warnings=warnings
                )
            else:
                # No balance, no transfers - nothing to report
                return self._create_empty_pnl_result(token)
        
        # FIFO queue for tracking positions
        buy_queue: List[FIFOPosition] = []
        realized_pnl = 0.0
        total_invested = 0.0
        positions_opened = 0
        positions_closed = 0
        
        # Process each transfer chronologically
        for i, t in enumerate(transfers):
            qty = abs(format_balance(t['delta_raw'], t['decimals']))
            usd_value = abs(t['delta_quote']) if t['delta_quote'] else 0.0
            gas_usd = t['gas_quote'] or 0.0
            
            # Validate quantity
            if qty <= 0:
                continue
            
            if t['transfer_type'] == 'IN':
                # BUY / RECEIVE
                positions_opened += 1
                
                # Price validation
                if usd_value == 0 or usd_value is None:
                    # Missing historical price - use current price as fallback
                    cost_per_unit = current_price
                    warnings.append(
                        f"Missing price data for transfer #{i+1} on {t['timestamp']}, "
                        f"using current price ${current_price:.6f}"
                    )
                    if self.config.verbose:
                        print(f"  ⚠️  {ticker}: No historical price for IN transfer, using current price")
                else:
                    # Include gas in cost basis
                    cost_per_unit = (usd_value + gas_usd) / qty
                
                buy_queue.append({
                    'qty': qty,
                    'cost_per_unit': cost_per_unit,
                    'gas_usd': gas_usd
                })
                
                total_invested += usd_value + gas_usd
                
            elif t['transfer_type'] == 'OUT':
                # SELL / SEND
                if not buy_queue:
                    warnings.append(
                        f"Sell without prior buy detected (transfer #{i+1}). "
                        f"Possible incomplete history."
                    )
                    if self.config.verbose:
                        print(f"  ⚠️  {ticker}: Selling from empty queue - history may be incomplete")
                    continue
                
                positions_closed += 1
                sell_qty = qty
                sell_value_usd = usd_value
                sell_gas_usd = gas_usd
                
                # Price validation for sells
                if sell_value_usd == 0:
                    # For sends to other wallets, use current price
                    sell_value_usd = sell_qty * current_price
                    warnings.append(
                        f"No sale price for transfer #{i+1}, using current price"
                    )
                
                # FIFO matching
                remaining_sell = sell_qty
                
                while remaining_sell > 0 and buy_queue:
                    position = buy_queue[0]
                    sell_from_this = min(remaining_sell, position['qty'])
                    
                    # Calculate PNL for this portion
                    entry_cost = sell_from_this * position['cost_per_unit']
                    exit_value = sell_from_this * safe_divide(sell_value_usd, sell_qty)
                    gas_portion = sell_gas_usd * safe_divide(sell_from_this, sell_qty)
                    
                    pnl_this = exit_value - entry_cost - gas_portion
                    realized_pnl += pnl_this
                    
                    # Update queue
                    remaining_sell -= sell_from_this
                    position['qty'] -= sell_from_this
                    
                    if position['qty'] <= 0:
                        buy_queue.pop(0)
                
                # If we couldn't match all sells, issue warning
                if remaining_sell > 0:
                    warnings.append(
                        f"Sold more than bought ({remaining_sell:.6f} {ticker} unmatched). "
                        f"History may be incomplete."
                    )
        
        # Calculate unrealized PNL from remaining positions
        remaining_qty = sum(p['qty'] for p in buy_queue)
        remaining_cost = sum(p['qty'] * p['cost_per_unit'] for p in buy_queue)
        
        # Balance reconciliation
        tolerance = current_balance * self.config.price_tolerance
        if not is_approximately_equal(remaining_qty, current_balance, tolerance):
            diff = abs(remaining_qty - current_balance)
            diff_pct = (diff / current_balance * 100) if current_balance > 0 else 0
            
            warnings.append(
                f"Balance mismatch: Queue={remaining_qty:.6f}, "
                f"Actual={current_balance:.6f}, "
                f"Diff={diff:.6f} ({diff_pct:.2f}%)"
            )
            
            if self.config.verbose:
                print(f"  ⚠️  {ticker}: Balance mismatch detected")
        
        # Use actual balance for unrealized PNL (more accurate)
        avg_cost_basis = safe_divide(remaining_cost, remaining_qty)
        unrealized_pnl = (current_price - avg_cost_basis) * current_balance
        
        return self._create_pnl_result(
            token=token,
            avg_cost_basis=avg_cost_basis,
            total_invested=total_invested,
            realized_pnl=realized_pnl,
            unrealized_pnl=unrealized_pnl,
            positions_opened=positions_opened,
            positions_closed=positions_closed,
            warnings=warnings
        )
    
    def _create_pnl_result(
        self,
        token: TokenAsset,
        avg_cost_basis: float,
        total_invested: float,
        realized_pnl: float,
        unrealized_pnl: float,
        positions_opened: int,
        positions_closed: int,
        warnings: List[str]
    ) -> TokenPNL:
        """Create a TokenPNL result with all calculations."""
        current_value = token['current_value']
        total_pnl = realized_pnl + unrealized_pnl
        
        # Calculate ROI
        if total_invested > 0:
            roi_percent = calculate_roi(total_invested, current_value + realized_pnl)
        else:
            roi_percent = 0.0
        
        return {
            'ticker': token['ticker'],
            'address': token['address'],
            'current_balance': round(token['balance'], 6),
            'current_price': round(token['current_price'], 6),
            'current_value': round(current_value, 2),
            'avg_cost_basis': round(avg_cost_basis, 6),
            'total_invested': round(total_invested, 2),
            'realized_pnl': round(realized_pnl, 2),
            'unrealized_pnl': round(unrealized_pnl, 2),
            'total_pnl': round(total_pnl, 2),
            'roi_percent': round(roi_percent, 2),
            'positions_opened': positions_opened,
            'positions_closed': positions_closed,
            'has_warnings': len(warnings) > 0,
            'warnings': warnings,
        }
    
    def _create_empty_pnl_result(self, token: TokenAsset) -> TokenPNL:
        """Create an empty PNL result for tokens with no activity."""
        return {
            'ticker': token['ticker'],
            'address': token['address'],
            'current_balance': 0.0,
            'current_price': round(token['current_price'], 6),
            'current_value': 0.0,
            'avg_cost_basis': 0.0,
            'total_invested': 0.0,
            'realized_pnl': 0.0,
            'unrealized_pnl': 0.0,
            'total_pnl': 0.0,
            'roi_percent': 0.0,
            'positions_opened': 0,
            'positions_closed': 0,
            'has_warnings': False,
            'warnings': [],
        }
