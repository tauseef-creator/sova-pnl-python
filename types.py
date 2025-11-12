"""
Type definitions for PNL Calculator.
Based on Covalent API response structures.
"""

from typing import TypedDict, Optional, List, Literal
from datetime import datetime


# ============================================================================
# Token & Balance Types
# ============================================================================

class TokenAsset(TypedDict):
    """Represents a token asset from balance fetch."""
    ticker: str
    address: str
    balance: float
    current_price: float
    current_value: float
    type: str
    native: bool
    decimals: int


class WalletBalances(TypedDict):
    """Response structure from fetch_balances."""
    wallet: str
    chain: str
    updated_at: datetime
    assets: List[TokenAsset]


# ============================================================================
# Transfer & Transaction Types
# ============================================================================

TransferType = Literal["IN", "OUT"]


class TokenTransfer(TypedDict):
    """Represents a single token transfer."""
    tx_hash: str
    timestamp: datetime
    transfer_type: TransferType
    delta_raw: int  # Raw amount (wei/smallest unit)
    delta_quote: float  # USD value at time of transfer
    gas_quote: float  # Gas cost in USD
    decimals: int
    successful: Optional[bool]


# ============================================================================
# PNL Calculation Types
# ============================================================================

class FIFOPosition(TypedDict):
    """FIFO queue position entry."""
    qty: float
    cost_per_unit: float
    gas_usd: float


class TokenPNL(TypedDict):
    """PNL calculation result for a single token."""
    ticker: str
    address: str
    current_balance: float
    current_price: float
    current_value: float
    avg_cost_basis: float
    total_invested: float
    realized_pnl: float
    unrealized_pnl: float
    total_pnl: float
    roi_percent: float
    positions_opened: int
    positions_closed: int
    has_warnings: bool
    warnings: List[str]


class WalletPNL(TypedDict):
    """Aggregated PNL for an entire wallet."""
    wallet: str
    chain: str
    tokens: List[TokenPNL]
    total_invested: float
    total_current_value: float
    total_realized_pnl: float
    total_unrealized_pnl: float
    total_pnl: float
    total_roi_percent: float


# ============================================================================
# Configuration Types
# ============================================================================

class PNLConfig(TypedDict):
    """Configuration for PNL calculator."""
    api_key: str
    quote_currency: str
    chains: List[str]
    wallets: List[str]
    include_nfts: bool
    no_spam: bool
    verbose: bool
    max_pages: int
    price_tolerance: float  # Tolerance for missing prices (0.0-1.0)


# ============================================================================
# Error & Warning Types
# ============================================================================

class PriceWarning(TypedDict):
    """Warning about price data issues."""
    token: str
    timestamp: datetime
    issue: str
    severity: Literal["low", "medium", "high"]


class BalanceMismatch(TypedDict):
    """Warning about balance reconciliation issues."""
    token: str
    queue_balance: float
    actual_balance: float
    difference: float
    percentage: float
