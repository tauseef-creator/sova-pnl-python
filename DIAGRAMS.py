"""
Visual Flow Diagram - How the PNL Calculator Works
ASCII art representation of the complete data flow
"""

EXECUTION_FLOW = """
┌─────────────────────────────────────────────────────────────────────┐
│                         EXECUTION FLOW                              │
└─────────────────────────────────────────────────────────────────────┘

1. START: main_v2.py
   │
   ├─→ Load Configuration (config.py)
   │   ├─ API Key
   │   ├─ Wallet Addresses
   │   ├─ Blockchain Chains
   │   └─ Settings (verbose, max_pages, etc.)
   │
   ├─→ Initialize Calculator (pnl_calculator.py)
   │   └─→ Create API Client (api_client.py)
   │       └─→ Connect to Covalent API
   │
   ├─→ For Each Wallet + Chain Combination:
   │   │
   │   ├─→ STEP 1: Fetch Current Balances
   │   │   │
   │   │   └─→ api_client.fetch_balances()
   │   │       ├─ Query: GET /balances/{chain}/{wallet}
   │   │       ├─ Filters: No spam, no zero balances
   │   │       └─ Returns: List[TokenAsset]
   │   │           ├─ ticker (e.g., "ETH")
   │   │           ├─ balance (e.g., 5.234)
   │   │           ├─ current_price (e.g., $3,250)
   │   │           └─ current_value (e.g., $17,012)
   │   │
   │   ├─→ STEP 2: For Each Token:
   │   │   │
   │   │   ├─→ Fetch Transfer History
   │   │   │   │
   │   │   │   ├─→ If Native Token (ETH, MATIC, BNB):
   │   │   │   │   └─→ api_client.fetch_native_transfers()
   │   │   │   │       ├─ Query: GET /transactions/{chain}/{wallet}
   │   │   │   │       ├─ Pagination: Loop through all pages
   │   │   │   │       ├─ Filter: Successful transactions only
   │   │   │   │       └─ Returns: List[TokenTransfer]
   │   │   │   │
   │   │   │   └─→ If ERC20 Token:
   │   │   │       └─→ api_client.fetch_erc20_transfers()
   │   │   │           ├─ Query: GET /transfers/{chain}/{wallet}/{token}
   │   │   │           ├─ Pagination: Loop through all pages
   │   │   │           └─ Returns: List[TokenTransfer]
   │   │   │
   │   │   └─→ Calculate PNL
   │   │       │
   │   │       └─→ pnl_engine.calculate_token_pnl()
   │   │           │
   │   │           ├─→ Sort transfers by timestamp (oldest first)
   │   │           │
   │   │           ├─→ FIFO Processing:
   │   │           │   │
   │   │           │   ├─→ For each "IN" transfer:
   │   │           │   │   ├─ Calculate cost_per_unit
   │   │           │   │   ├─ Validate price (fallback if missing)
   │   │           │   │   ├─ Add to FIFO queue
   │   │           │   │   └─ Track total_invested
   │   │           │   │
   │   │           │   └─→ For each "OUT" transfer:
   │   │           │       ├─ Match with oldest position (FIFO)
   │   │           │       ├─ Calculate realized PNL
   │   │           │       ├─ Remove from queue
   │   │           │       └─ Accumulate realized_pnl
   │   │           │
   │   │           ├─→ Calculate Unrealized PNL:
   │   │           │   ├─ remaining_qty = sum(queue)
   │   │           │   ├─ avg_cost_basis = avg(queue prices)
   │   │           │   └─ unrealized_pnl = (current_price - avg_cost) × balance
   │   │           │
   │   │           ├─→ Validate Balance:
   │   │           │   ├─ Compare queue vs actual balance
   │   │           │   └─ Generate warnings if mismatch
   │   │           │
   │   │           └─→ Return TokenPNL:
   │   │               ├─ realized_pnl
   │   │               ├─ unrealized_pnl
   │   │               ├─ total_pnl
   │   │               ├─ roi_percent
   │   │               └─ warnings[]
   │   │
   │   └─→ STEP 3: Aggregate to WalletPNL
   │       ├─ Sum all token PNLs
   │       ├─ Calculate total ROI
   │       └─ Return WalletPNL
   │
   ├─→ Display Results (pnl_calculator.py)
   │   ├─ Per-token breakdown
   │   ├─ Per-wallet totals
   │   └─ Grand total
   │
   └─→ Export to JSON (main_v2.py)
       └─ Save to pnl_results.json

END
"""

DATA_STRUCTURES = """
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA STRUCTURES FLOW                           │
└─────────────────────────────────────────────────────────────────────┘

API Response → Internal Type → Calculation → Final Result

┌──────────────────┐
│ Covalent API     │
│ BalancesResponse │
└────────┬─────────┘
         │
         │ Transform
         ▼
┌──────────────────┐      ┌──────────────────┐
│ TokenAsset       │      │ TokenTransfer    │
├──────────────────┤      ├──────────────────┤
│ ticker: str      │      │ tx_hash: str     │
│ balance: float   │◄─────┤ timestamp: date  │
│ current_price: $ │      │ transfer_type: IN│
│ current_value: $ │      │ delta_raw: int   │
│ address: str     │      │ delta_quote: $   │
│ decimals: int    │      │ gas_quote: $     │
└────────┬─────────┘      └────────┬─────────┘
         │                         │
         │                         │
         │      FIFO Engine        │
         └────────┬────────────────┘
                  │
                  │ Calculate PNL
                  ▼
         ┌────────────────┐
         │ FIFOPosition   │ (Internal Queue)
         ├────────────────┤
         │ qty: float     │
         │ cost_per_unit:$│
         │ gas_usd: $     │
         └────────┬───────┘
                  │
                  │ Aggregate
                  ▼
         ┌────────────────────┐
         │ TokenPNL           │
         ├────────────────────┤
         │ ticker: str        │
         │ current_balance: # │
         │ current_price: $   │
         │ avg_cost_basis: $  │
         │ realized_pnl: $    │
         │ unrealized_pnl: $  │
         │ total_pnl: $       │
         │ roi_percent: %     │
         │ warnings: []       │
         └────────┬───────────┘
                  │
                  │ Aggregate
                  ▼
         ┌────────────────────┐
         │ WalletPNL          │
         ├────────────────────┤
         │ wallet: address    │
         │ chain: string      │
         │ tokens: []         │
         │ total_invested: $  │
         │ total_pnl: $       │
         │ total_roi: %       │
         └────────────────────┘
"""

MODULE_DEPENDENCIES = """
┌─────────────────────────────────────────────────────────────────────┐
│                     MODULE DEPENDENCIES                             │
└─────────────────────────────────────────────────────────────────────┘

Level 0 (No Dependencies):
┌──────────┐  ┌──────────┐  ┌──────────┐
│ types.py │  │ utils.py │  │config.py │
└──────────┘  └──────────┘  └──────────┘

Level 1 (Depends on Level 0):
         ┌────────────────┐
         │ api_client.py  │
         ├────────────────┤
         │ Imports:       │
         │ - types        │
         │ - utils        │
         │ - config       │
         └────────────────┘

         ┌────────────────┐
         │ pnl_engine.py  │
         ├────────────────┤
         │ Imports:       │
         │ - types        │
         │ - utils        │
         │ - config       │
         └────────────────┘

Level 2 (Depends on Level 0 & 1):
         ┌──────────────────┐
         │pnl_calculator.py │
         ├──────────────────┤
         │ Imports:         │
         │ - types          │
         │ - utils          │
         │ - config         │
         │ - api_client     │
         │ - pnl_engine     │
         └──────────────────┘

Level 3 (Entry Point):
         ┌──────────────────┐
         │   main_v2.py     │
         ├──────────────────┤
         │ Imports:         │
         │ - config         │
         │ - pnl_calculator │
         │ - types          │
         └──────────────────┘

Direction: Top → Bottom (No circular dependencies)
"""

FIFO_CALCULATION = """
┌─────────────────────────────────────────────────────────────────────┐
│                    FIFO CALCULATION EXAMPLE                         │
└─────────────────────────────────────────────────────────────────────┘

Scenario: Trading ETH

Step 1: BUY 100 ETH @ $1,000
┌──────────────────────┐
│ FIFO Queue           │
├──────────────────────┤
│ 100 ETH @ $1,000     │
└──────────────────────┘
Cost Basis: $100,000
Realized PNL: $0

Step 2: BUY 50 ETH @ $1,500
┌──────────────────────┐
│ FIFO Queue           │
├──────────────────────┤
│ 100 ETH @ $1,000     │ ← Oldest (FIFO)
│  50 ETH @ $1,500     │
└──────────────────────┘
Total Invested: $175,000
Realized PNL: $0

Step 3: SELL 120 ETH @ $2,000
┌──────────────────────┐
│ FIFO Queue           │
├──────────────────────┤
│ ~~100 ETH @ $1,000~~ │ ← Sold (match oldest first)
│ ~~20 ETH @ $1,500~~  │ ← Partially sold
│  30 ETH @ $1,500     │ ← Remaining
└──────────────────────┘

Calculation:
- Sell 100 @ $2,000 (from first position):
  Revenue: 100 × $2,000 = $200,000
  Cost: 100 × $1,000 = $100,000
  PNL: $100,000

- Sell 20 @ $2,000 (from second position):
  Revenue: 20 × $2,000 = $40,000
  Cost: 20 × $1,500 = $30,000
  PNL: $10,000

Total Realized PNL: $110,000

Step 4: Current Holdings
┌──────────────────────┐
│ FIFO Queue           │
├──────────────────────┤
│  30 ETH @ $1,500     │
└──────────────────────┘
Current Price: $2,500

Unrealized PNL:
- Holdings: 30 ETH
- Cost Basis: $1,500 (avg of remaining)
- Current Price: $2,500
- Unrealized: 30 × ($2,500 - $1,500) = $30,000

TOTAL PNL:
- Realized: $110,000
- Unrealized: $30,000
- Total: $140,000
- ROI: $140,000 / $175,000 = 80%
"""

ERROR_HANDLING = """
┌─────────────────────────────────────────────────────────────────────┐
│                      ERROR HANDLING FLOW                            │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│ User Input      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Config          │
│ Validation      │
├─────────────────┤
│ ✓ API key valid │
│ ✓ Wallet format │
│ ✓ Chain exists  │
└────────┬────────┘
         │
         │ If invalid
         ├──────────► ValueError: "Invalid config"
         │
         ▼ If valid
┌─────────────────┐
│ API Call        │
└────────┬────────┘
         │
         ├─→ Success
         │   └─→ Continue
         │
         ├─→ Network Error
         │   └──► Retry with backoff
         │
         ├─→ Rate Limit (429)
         │   └──► Wait 60s, retry
         │
         └─→ API Error
             └──► Log error, skip token
                  Continue with others

┌─────────────────┐
│ Data Processing │
└────────┬────────┘
         │
         ├─→ Missing Price
         │   └──► Warning + Fallback to current price
         │
         ├─→ Balance Mismatch
         │   └──► Warning + Use actual balance
         │
         ├─→ Sell without Buy
         │   └──► Warning + Skip transaction
         │
         └─→ Failed Transaction
             └──► Filter out, continue

Result: Graceful degradation, comprehensive warnings
"""

def print_diagrams():
    """Print all diagrams."""
    print(EXECUTION_FLOW)
    print("\n" + "="*70 + "\n")
    print(DATA_STRUCTURES)
    print("\n" + "="*70 + "\n")
    print(MODULE_DEPENDENCIES)
    print("\n" + "="*70 + "\n")
    print(FIFO_CALCULATION)
    print("\n" + "="*70 + "\n")
    print(ERROR_HANDLING)


if __name__ == "__main__":
    print_diagrams()
