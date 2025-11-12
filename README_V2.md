# Blockchain Wallet PNL Calculator

Production-ready PNL (Profit and Loss) calculator for blockchain wallets with comprehensive type safety, validation, and error handling.

## 🎯 Features

### ✅ **Fixed Issues from Original Implementation**
- ✅ **Native Transfer Logic Bug**: Now properly checks both `from_address` and `to_address` 
- ✅ **Missing Price Validation**: Handles zero/missing historical prices with fallbacks
- ✅ **Balance Reconciliation**: Validates FIFO queue vs actual balance
- ✅ **Sold-Out Positions**: Tracks realized PNL even for fully sold tokens
- ✅ **Failed Transactions**: Filters out failed transactions
- ✅ **Comprehensive Typing**: Full type hints based on Covalent API structures

### 🚀 **New Features**
- **Multi-chain Support**: Analyze wallets across multiple blockchains
- **FIFO Cost Basis**: Accurate tax-compliant PNL calculations
- **Gas Fee Accounting**: Includes gas costs in cost basis
- **Warning System**: Alerts for data quality issues
- **ROI Calculation**: Return on investment percentages
- **Export to JSON**: Save results for record keeping
- **Verbose Logging**: Detailed progress tracking

## 📁 Project Structure

```
pnl-python/
├── config.py           # Configuration management with validation
├── types.py            # TypedDict definitions for all data structures
├── utils.py            # Reusable utility functions
├── api_client.py       # Typed wrapper for Covalent API
├── pnl_engine.py       # Core PNL calculation engine
├── pnl_calculator.py   # High-level orchestrator
├── main_v2.py          # Main executable script
└── main.py             # Original implementation (for reference)
```

## 🔧 Installation

### Prerequisites
```bash
# Python 3.8+
python --version

# Install dependencies
pip install covalent-api-sdk
```

### Setup
1. Get a free API key from [Covalent](https://www.covalenthq.com/)
2. Edit `main_v2.py` and add your API key and wallet addresses

## 🚀 Usage

### Basic Usage

```python
from config import Config
from pnl_calculator import WalletPNLCalculator

# Configure
config = Config(
    api_key="cqt_YOUR_API_KEY_HERE",
    wallets=["0xYourWalletAddress"],
    chains=["eth-mainnet"],
    verbose=True
)

# Calculate
calculator = WalletPNLCalculator(config)
results = calculator.calculate_all()
```

### Run from Command Line

```bash
# Edit main_v2.py with your config, then:
python main_v2.py
```

### Environment Variables

```bash
export COVALENT_API_KEY="cqt_..."
export PNL_WALLETS="0x...,0x..."
export PNL_CHAINS="eth-mainnet,polygon-mainnet"

python main_v2.py
```

## 📊 How It Works

### Step-by-Step Flow

1. **Fetch Current Balances**
   - Queries Covalent API for current token holdings
   - Filters spam tokens and zero balances

2. **Fetch Transfer History**
   - For native tokens: Uses transaction history API
   - For ERC20: Uses token transfer API
   - Properly handles pagination

3. **Calculate Cost Basis (FIFO)**
   ```
   For each transfer:
   ├─ IN:  Add to FIFO queue with cost basis
   └─ OUT: Match with oldest position, calculate realized PNL
   ```

4. **Calculate Unrealized PNL**
   ```
   Unrealized PNL = (Current Price - Avg Cost Basis) × Current Balance
   ```

5. **Aggregate Results**
   ```
   Total PNL = Realized PNL + Unrealized PNL
   ROI % = (Total PNL / Total Invested) × 100
   ```

## 📝 Example Output

```
======================================================================
BLOCKCHAIN WALLET PNL CALCULATOR
======================================================================
Chains: eth-mainnet
Wallets: 1
Quote Currency: USD
======================================================================

======================================================================
WALLET: 0xf29C...0b675 | CHAIN: eth-mainnet
======================================================================

Found 5 tokens with non-zero balances
Updated at: 2025-11-12 10:30:45 UTC

→ ETH      | Balance:    5.234567 | Price: $3,250.00
  Fetched 234 transfers
  ├─ Cost Basis: $2,890.50
  ├─ Invested:   $15,234.00
  ├─ Value Now:  $17,012.34
  ├─ Realized:   $1,450.00
  ├─ Unrealized: $1,882.34
  ├─ Total PNL:  $3,332.34 (+21.87%)
  └─ Positions:  12 opened, 7 closed

→ USDC     | Balance: 1000.000000 | Price: $1.00
  Fetched 45 transfers
  ├─ Cost Basis: $1.00
  ├─ Invested:   $1,000.00
  ├─ Value Now:  $1,000.00
  ├─ Realized:   $0.00
  ├─ Unrealized: $0.00
  ├─ Total PNL:  $0.00 (+0.00%)
  └─ Positions:  2 opened, 0 closed

======================================================================
FINAL SUMMARY
======================================================================
0xf29C...0b675 | eth-mainnet        | PNL:    $3,332.34 | ROI:    +21.87%
======================================================================

💾 Results exported to pnl_results.json
```

## ⚠️ Important Notes

### Price Data
- **Historical Prices**: Covalent provides USD value at transaction time
- **Missing Prices**: Falls back to current price with warning
- **Gas Fees**: Included in cost basis for buys, subtracted from proceeds on sells

### FIFO Accounting
- **First In, First Out**: Tax-compliant cost basis method
- **Queue Tracking**: Maintains purchase queue for accurate matching
- **Balance Validation**: Warns if queue doesn't match actual balance

### Warnings
The calculator will warn you about:
- Missing historical price data
- Balance mismatches (incomplete history)
- Sells without prior buys (missing early transactions)
- Failed transactions (automatically filtered)

## 🔍 Type Safety

All data structures are fully typed:

```python
from types import TokenPNL

pnl: TokenPNL = {
    'ticker': 'ETH',
    'current_balance': 5.234,
    'current_price': 3250.00,
    'avg_cost_basis': 2890.50,
    'realized_pnl': 1450.00,
    'unrealized_pnl': 1882.34,
    'total_pnl': 3332.34,
    'roi_percent': 21.87,
    # ... more fields
}
```

## 🎛️ Configuration Options

```python
Config(
    api_key: str,              # Required: Covalent API key
    quote_currency: str,       # Default: "USD"
    chains: List[str],         # Default: ["eth-mainnet"]
    wallets: List[str],        # Required: Wallet addresses
    include_nfts: bool,        # Default: False
    no_spam: bool,             # Default: True
    verbose: bool,             # Default: False
    max_pages: int,            # Default: 1000
    price_tolerance: float,    # Default: 0.01 (1%)
)
```

### Supported Chains
- `eth-mainnet` - Ethereum
- `matic-mainnet` - Polygon
- `bsc-mainnet` - BNB Chain
- `avalanche-mainnet` - Avalanche
- `arbitrum-mainnet` - Arbitrum
- `optimism-mainnet` - Optimism
- `base-mainnet` - Base
- And more...

## 🐛 Troubleshooting

### Issue: "Invalid API key"
**Solution**: Get a free API key from https://www.covalenthq.com/

### Issue: "Balance mismatch" warnings
**Cause**: Incomplete transaction history (wallet created before Covalent indexing)
**Solution**: This is informational - PNL calculations use actual balance

### Issue: "No price data" warnings
**Cause**: Covalent doesn't have historical price for that timestamp
**Solution**: Calculator uses current price as fallback

### Issue: Rate limiting (429 errors)
**Solution**: Increase `rate_limit_pause` in config or reduce `max_pages`

## 📦 Module Reference

### `config.py`
Configuration management with validation

### `types.py`
TypedDict definitions for:
- `TokenAsset` - Token balance data
- `TokenTransfer` - Transfer/transaction data
- `TokenPNL` - PNL calculation result
- `WalletPNL` - Aggregated wallet PNL

### `utils.py`
Helper functions:
- `format_balance()` - Convert wei to decimals
- `format_currency()` - Pretty print money
- `format_percentage()` - Pretty print percentages
- `calculate_roi()` - ROI calculation
- `is_address_equal()` - Case-insensitive address comparison

### `api_client.py`
Covalent API wrapper:
- `fetch_balances()` - Get current holdings
- `fetch_native_transfers()` - Get ETH/native transfers
- `fetch_erc20_transfers()` - Get token transfers
- `fetch_token_transfers()` - Unified interface

### `pnl_engine.py`
Core calculation engine:
- `calculate_token_pnl()` - FIFO-based PNL with validation

### `pnl_calculator.py`
High-level orchestrator:
- `calculate_wallet_pnl()` - Single wallet calculation
- `calculate_all()` - All wallets across all chains

## 🔐 Security

- **Never commit API keys**: Use environment variables
- **Read-only**: This tool only reads blockchain data
- **No private keys**: Only uses public wallet addresses

## 📄 License

MIT License - Feel free to use and modify!

## 🙋 Support

For issues or questions:
1. Check the troubleshooting section
2. Review Covalent API docs: https://www.covalenthq.com/docs/
3. Examine warning messages in verbose mode

## 🎯 Comparison with Original

### Original `main.py`
- ❌ Native transfer bug (missing from_address check)
- ❌ No price validation
- ❌ No type safety
- ❌ Limited error handling
- ✅ Basic FIFO implementation

### New `main_v2.py` + modules
- ✅ Fixed all critical bugs
- ✅ Comprehensive type safety
- ✅ Price validation with fallbacks
- ✅ Balance reconciliation
- ✅ Warning system
- ✅ Clean architecture
- ✅ Production-ready error handling

---

**Built with ❤️ for accurate crypto PNL tracking**
