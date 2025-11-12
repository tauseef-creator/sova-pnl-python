#!/usr/bin/env python3
"""
Main executable for PNL Calculator.

Usage:
    # Basic usage
    python main.py
    
    # With environment variables
    export COVALENT_API_KEY="cqt_..."
    export PNL_WALLETS="0x...,0x..."
    export PNL_CHAINS="eth-mainnet,polygon-mainnet"
    python main.py
"""

import sys
from typing import List

from config import Config
from pnl_calculator import WalletPNLCalculator
from pnl_types import WalletPNL


def main() -> int:
    """
    Main entry point for PNL calculator.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Configuration
        # You can either:
        # 1. Set environment variables (see Config.from_env())
        # 2. Or configure directly here:
        
        config = Config(
            api_key="cqt_rQRKdJKWqr888G3hK6bHcHXFGwf3",  # Replace with your API key
            quote_currency="USD",
            chains=["eth-mainnet"],  # Add more chains as needed
            wallets=[
                "0xf29C6705F188526E0029A92EE6bc21Ebc750b675"  # Add your wallet addresses
            ],
            include_nfts=False,
            no_spam=True,
            verbose=True,  # Set to False for quiet mode
            max_pages=1000,
            price_tolerance=0.01,
        )
        
        # Alternative: Load from environment
        # config = Config.from_env()
        
        # Initialize calculator
        calculator = WalletPNLCalculator(config)
        
        # Run calculations
        results: List[WalletPNL] = calculator.calculate_all()
        
        # Optional: Export results to JSON
        if results:
            export_to_json(results, "pnl_results.json")
        
        return 0
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}", file=sys.stderr)
        return 1
    
    except KeyboardInterrupt:
        print("\n\n⏸️  Interrupted by user", file=sys.stderr)
        return 130
    
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def export_to_json(results: List[WalletPNL], filename: str) -> None:
    """
    Export results to JSON file.
    
    Args:
        results: List of WalletPNL results
        filename: Output filename
    """
    import json
    from datetime import datetime
    
    # Convert datetime objects to strings for JSON serialization
    def serialize(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    output = {
        'generated_at': datetime.now().isoformat(),
        'results': results,
    }
    
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2, default=serialize)
    
    print(f"\n💾 Results exported to {filename}")


if __name__ == "__main__":
    sys.exit(main())
