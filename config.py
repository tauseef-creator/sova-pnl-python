"""
Configuration management for PNL Calculator.
"""

from typing import List
from dataclasses import dataclass, field
import os


@dataclass
class Config:
    """
    Configuration for PNL Calculator.
    
    Attributes:
        api_key: Covalent API key
        quote_currency: Fiat currency for quotes (default: USD)
        chains: List of blockchain networks to query
        wallets: List of wallet addresses to analyze
        include_nfts: Whether to include NFTs in balance fetch
        no_spam: Filter out spam tokens
        verbose: Enable detailed logging
        max_pages: Maximum pages to fetch for transaction history
        price_tolerance: Tolerance for balance mismatches (0.0-1.0)
    """
    
    # Required
    api_key: str
    
    # Query Configuration
    quote_currency: str = "USD"
    chains: List[str] = field(default_factory=lambda: ["eth-mainnet"])
    wallets: List[str] = field(default_factory=list)
    
    # Filters
    include_nfts: bool = False
    no_spam: bool = True
    
    # Behavior
    verbose: bool = False
    max_pages: int = 1000
    price_tolerance: float = 0.01  # 1% tolerance
    
    # Rate Limiting
    rate_limit_pause: int = 1  # seconds between batches
    rate_limit_retry_wait: int = 60  # seconds to wait on 429
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate configuration values."""
        if not self.api_key:
            raise ValueError("API key is required")
        
        if not self.api_key.startswith("cqt_"):
            raise ValueError("Invalid Covalent API key format (should start with 'cqt_')")
        
        if not self.wallets:
            raise ValueError("At least one wallet address is required")
        
        if not self.chains:
            raise ValueError("At least one chain is required")
        
        if self.price_tolerance < 0 or self.price_tolerance > 1:
            raise ValueError("price_tolerance must be between 0 and 1")
        
        if self.max_pages < 1:
            raise ValueError("max_pages must be at least 1")
        
        # Validate wallet addresses (basic check)
        for wallet in self.wallets:
            if not wallet.startswith("0x") or len(wallet) != 42:
                raise ValueError(f"Invalid Ethereum address format: {wallet}")
    
    @classmethod
    def from_env(cls) -> "Config":
        """
        Create configuration from environment variables.
        
        Environment variables:
            COVALENT_API_KEY: API key (required)
            PNL_CHAINS: Comma-separated list of chains
            PNL_WALLETS: Comma-separated list of wallet addresses
            PNL_QUOTE_CURRENCY: Quote currency (default: USD)
            PNL_INCLUDE_NFTS: Include NFTs (true/false)
            PNL_NO_SPAM: Filter spam (true/false)
            PNL_VERBOSE: Enable verbose logging (true/false)
            
        Returns:
            Config instance
            
        Raises:
            ValueError: If required environment variables are missing
        """
        api_key = os.getenv("COVALENT_API_KEY")
        if not api_key:
            raise ValueError("COVALENT_API_KEY environment variable is required")
        
        chains_str = os.getenv("PNL_CHAINS", "eth-mainnet")
        chains = [c.strip() for c in chains_str.split(",") if c.strip()]
        
        wallets_str = os.getenv("PNL_WALLETS", "")
        wallets = [w.strip() for w in wallets_str.split(",") if w.strip()]
        
        return cls(
            api_key=api_key,
            quote_currency=os.getenv("PNL_QUOTE_CURRENCY", "USD"),
            chains=chains,
            wallets=wallets,
            include_nfts=os.getenv("PNL_INCLUDE_NFTS", "").lower() == "true",
            no_spam=os.getenv("PNL_NO_SPAM", "true").lower() == "true",
            verbose=os.getenv("PNL_VERBOSE", "").lower() == "true",
        )


# Supported blockchain networks
SUPPORTED_CHAINS = [
    "eth-mainnet",
    "matic-mainnet",
    "bsc-mainnet",
    "avalanche-mainnet",
    "arbitrum-mainnet",
    "optimism-mainnet",
    "base-mainnet",
    "polygon-zkevm-mainnet",
]
