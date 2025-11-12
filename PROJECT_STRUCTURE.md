# Project Structure Overview

## 📁 File Organization

```
pnl-python/
│
├── 📄 main.py                    # Original implementation (preserved for reference)
├── 🚀 main_v2.py                 # New main executable - START HERE
│
├── 📚 Core Modules
│   ├── config.py                 # Configuration & validation
│   ├── types.py                  # Type definitions (TypedDict)
│   ├── utils.py                  # Helper functions
│   ├── api_client.py             # Covalent API wrapper (typed)
│   ├── pnl_engine.py             # Core PNL calculation logic
│   └── pnl_calculator.py         # High-level orchestrator
│
├── 📖 Documentation
│   ├── README_V2.md              # Full documentation
│   ├── QUICK_START.md            # Get started in 5 minutes
│   ├── FIXES_APPLIED.md          # Technical fix details
│   └── PROJECT_STRUCTURE.md      # This file
│
└── 📊 Generated Files (after running)
    └── pnl_results.json          # Exported results
```

---

## 🔍 Module Details

### 🚀 **main_v2.py** - Entry Point
**Purpose**: Main executable script  
**What it does**:
- Loads configuration
- Initializes calculator
- Runs PNL calculations
- Exports results to JSON

**Key Code**:
```python
config = Config(api_key="...", wallets=["0x..."], ...)
calculator = WalletPNLCalculator(config)
results = calculator.calculate_all()
```

**When to edit**: To change your API key, wallets, or chains

---

### ⚙️ **config.py** - Configuration Management
**Purpose**: Centralized configuration with validation  
**What it does**:
- Stores all settings (API key, wallets, chains)
- Validates configuration on initialization
- Supports environment variables

**Key Classes**:
```python
@dataclass
class Config:
    api_key: str
    wallets: List[str]
    chains: List[str]
    verbose: bool
    # ... more settings
```

**When to edit**: To add new configuration options

---

### 📋 **types.py** - Type Definitions
**Purpose**: Type safety with TypedDict  
**What it does**:
- Defines structure of all data
- Enables IDE autocomplete
- Catches type errors early

**Key Types**:
```python
class TokenAsset(TypedDict):
    ticker: str
    balance: float
    current_price: float
    # ...

class TokenPNL(TypedDict):
    realized_pnl: float
    unrealized_pnl: float
    total_pnl: float
    # ...
```

**When to edit**: To add new fields to data structures

---

### 🛠️ **utils.py** - Utility Functions
**Purpose**: Reusable helper functions  
**What it does**:
- Format numbers (currency, percentages)
- Balance conversions (wei → decimals)
- Address comparisons
- Math helpers

**Key Functions**:
```python
def format_balance(balance: int, decimals: int) -> float
def format_currency(amount: float) -> str
def calculate_roi(invested: float, current: float) -> float
def is_address_equal(addr1: str, addr2: str) -> bool
```

**When to edit**: To add new formatting or calculation helpers

---

### 🌐 **api_client.py** - API Wrapper
**Purpose**: Typed wrapper around Covalent API  
**What it does**:
- Fetches balances from blockchain
- Fetches transfer history (native & ERC20)
- Handles pagination
- Manages rate limiting

**Key Methods**:
```python
class CovalentAPIClient:
    def fetch_balances(wallet, chain) -> WalletBalances
    def fetch_native_transfers(chain, wallet) -> List[TokenTransfer]
    def fetch_erc20_transfers(chain, wallet, token) -> List[TokenTransfer]
```

**Critical Fixes**:
- ✅ Fixed native transfer direction logic
- ✅ Filters failed transactions
- ✅ Proper from/to address checking

**When to edit**: To add new API endpoints or change fetch logic

---

### 🧮 **pnl_engine.py** - Calculation Engine
**Purpose**: Core PNL calculation with FIFO  
**What it does**:
- FIFO cost basis tracking
- Realized PNL calculation (from sells)
- Unrealized PNL calculation (from holdings)
- Price validation & fallbacks
- Balance reconciliation

**Key Method**:
```python
class PNLCalculator:
    def calculate_token_pnl(token, transfers) -> TokenPNL:
        # FIFO matching
        # Realized PNL calculation
        # Unrealized PNL calculation
        # Warning generation
```

**Critical Fixes**:
- ✅ Missing price validation
- ✅ Balance mismatch detection
- ✅ Sold-out position handling
- ✅ Warning system

**When to edit**: To change PNL calculation methodology (LIFO, average cost, etc.)

---

### 🎯 **pnl_calculator.py** - Orchestrator
**Purpose**: High-level workflow coordination  
**What it does**:
- Coordinates API calls
- Loops through wallets and chains
- Aggregates results
- Displays formatted output
- Manages error handling

**Key Methods**:
```python
class WalletPNLCalculator:
    def calculate_wallet_pnl(wallet, chain) -> WalletPNL
    def calculate_all() -> List[WalletPNL]
```

**When to edit**: To change workflow or output format

---

## 🔄 Data Flow

```
1. main_v2.py
   ↓ Creates config
   ↓ Initializes WalletPNLCalculator
   │
2. pnl_calculator.py (WalletPNLCalculator)
   ↓ For each wallet + chain:
   │
3. api_client.py (CovalentAPIClient)
   ↓ fetch_balances() → WalletBalances
   ↓ fetch_token_transfers() → List[TokenTransfer]
   │
4. pnl_engine.py (PNLCalculator)
   ↓ calculate_token_pnl() → TokenPNL
   │   ├─ Uses utils.py for formatting
   │   └─ Uses types.py for structure
   │
5. pnl_calculator.py
   ↓ Aggregates to WalletPNL
   ↓ Displays results
   │
6. main_v2.py
   └─ Exports to JSON
```

---

## 🎨 Dependency Graph

```
main_v2.py
    ├─→ config.py
    ├─→ pnl_calculator.py
    │       ├─→ api_client.py
    │       │       ├─→ config.py
    │       │       ├─→ types.py
    │       │       └─→ utils.py
    │       ├─→ pnl_engine.py
    │       │       ├─→ config.py
    │       │       ├─→ types.py
    │       │       └─→ utils.py
    │       ├─→ types.py
    │       └─→ utils.py
    └─→ types.py
```

**No circular dependencies** ✅

---

## 🔀 Import Chain

### From top to bottom:

```python
# main_v2.py
from config import Config
from pnl_calculator import WalletPNLCalculator
from types import WalletPNL

# pnl_calculator.py
from config import Config
from api_client import CovalentAPIClient
from pnl_engine import PNLCalculator
from types import WalletPNL, TokenPNL
from utils import format_currency, format_percentage, ...

# api_client.py
from covalent import CovalentClient  # External
from config import Config
from types import TokenAsset, WalletBalances, TokenTransfer
from utils import format_balance, is_address_equal

# pnl_engine.py
from config import Config
from types import TokenAsset, TokenTransfer, TokenPNL, FIFOPosition
from utils import format_balance, calculate_roi, is_approximately_equal

# config.py (no internal imports)
# types.py (no internal imports)
# utils.py (no internal imports)
```

---

## 📝 Modification Guide

### To add a new blockchain:

1. **config.py**: Add to `SUPPORTED_CHAINS`
2. **main_v2.py**: Add to `chains=["new-chain"]`
3. No other changes needed! ✨

### To change PNL calculation method (e.g., LIFO):

1. **pnl_engine.py**: Modify `calculate_token_pnl()`
2. Change queue logic from FIFO to LIFO
3. Update docstrings

### To add new warnings:

1. **types.py**: Add new warning type if needed
2. **pnl_engine.py**: Add warning detection logic
3. **pnl_calculator.py**: Update display if needed

### To add new output format (CSV, Excel):

1. **main_v2.py**: Add new export function
2. Use `results` from `calculate_all()`
3. Format as needed

---

## 🧪 Testing Strategy

### Unit Tests (recommended to add):

```python
# test_utils.py
def test_format_balance():
    assert format_balance(1000000000000000000, 18) == 1.0
    assert format_balance(1000000, 6) == 1.0

# test_pnl_engine.py
def test_simple_buy_hold():
    token = {'ticker': 'ETH', 'balance': 1.0, 'current_price': 2000}
    transfers = [{'type': 'IN', 'qty': 1.0, 'price': 1500}]
    result = calculator.calculate_token_pnl(token, transfers)
    assert result['unrealized_pnl'] == 500.0
```

### Integration Tests:

```python
# test_full_flow.py
def test_wallet_pnl():
    config = Config(api_key="test", wallets=["0x..."])
    calculator = WalletPNLCalculator(config)
    results = calculator.calculate_all()
    assert len(results) > 0
```

---

## 🔧 Maintenance Checklist

- [ ] Keep API key secure (use environment variables)
- [ ] Update dependencies: `pip install --upgrade covalent-api-sdk`
- [ ] Monitor Covalent API changes
- [ ] Add tests for critical functions
- [ ] Document any custom modifications
- [ ] Export results regularly for backup
- [ ] Review warnings in verbose output

---

## 📊 Code Statistics

| Module | Lines | Purpose |
|--------|-------|---------|
| `main_v2.py` | ~110 | Entry point |
| `config.py` | ~130 | Configuration |
| `types.py` | ~110 | Type defs |
| `utils.py` | ~200 | Helpers |
| `api_client.py` | ~310 | API calls |
| `pnl_engine.py` | ~270 | Core logic |
| `pnl_calculator.py` | ~250 | Orchestration |
| **TOTAL** | **~1,380** | Production code |

---

## 🎓 Learning Path

**If you're new to this codebase:**

1. Start: `QUICK_START.md` - Run it first
2. Next: `README_V2.md` - Understand features
3. Then: `main_v2.py` - See the entry point
4. Study: `types.py` - Learn data structures
5. Read: `pnl_calculator.py` - Understand flow
6. Deep dive: `pnl_engine.py` - Core calculations
7. Advanced: `FIXES_APPLIED.md` - Technical details

---

**Questions?**
- Check the documentation files
- Look at code comments
- Review type hints
- Enable verbose mode to see what's happening

Happy coding! 🚀
