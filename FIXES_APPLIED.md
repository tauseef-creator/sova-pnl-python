# Critical Fixes Applied to PNL Calculator

## Summary of Changes

This document details all the critical fixes applied to transform the original PNL calculator into a production-ready tool.

---

## 🐛 Bug Fix #1: Native Transfer Direction Logic

### **Original Code (BROKEN)**
```python
# In fetch_native_transfers()
is_in = tx.to_address and tx.to_address.lower() == wallet.lower()
transfer_type = "IN" if is_in else "OUT"
```

### **Problem**
- Only checks if transaction is incoming (`to_address == wallet`)
- Assumes ALL other transactions are outgoing
- **FAILS** when wallet is neither sender nor receiver
- Results in incorrect PNL calculations

### **Fixed Code**
```python
# In api_client.py - fetch_native_transfers()
is_incoming = is_address_equal(tx.to_address, wallet)
is_outgoing = is_address_equal(tx.from_address, wallet)

# Skip if wallet not involved
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
```

### **Impact**
- ✅ Correctly identifies transaction direction
- ✅ Skips transactions where wallet isn't involved
- ✅ Accurate IN/OUT classification
- ✅ Correct delta signs for calculations

---

## 🐛 Bug Fix #2: Missing Price Validation

### **Original Code (BROKEN)**
```python
# In calculate_token_pnl()
if t['transfer_type'] == 'IN':
    cost_per_unit = (usd_value + gas_usd) / qty if qty > 0 else 0.0
```

### **Problem**
- If `usd_value` is 0 or None (missing historical price)
- Sets cost basis to 0
- **MASSIVELY INFLATES** PNL calculations
- No warning to user

### **Fixed Code**
```python
# In pnl_engine.py - calculate_token_pnl()
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
    cost_per_unit = (usd_value + gas_usd) / qty
```

### **Impact**
- ✅ Detects missing price data
- ✅ Falls back to current price
- ✅ Warns user about data quality
- ✅ Prevents inflated PNL numbers

---

## 🐛 Bug Fix #3: Zero Balance Token Skip

### **Original Code (BROKEN)**
```python
if current_balance == 0:
    return {
        'ticker': ticker,
        'realized_pnl': 0.0,
        'unrealized_pnl': 0.0,
        ...
    }
```

### **Problem**
- If you bought AND sold ALL of a token
- You have realized PNL but zero balance
- **LOSES ALL REALIZED PNL** data
- User never sees profits from sold positions

### **Fixed Code**
```python
# In pnl_engine.py
if not transfers:
    if current_balance > 0:
        warnings.append(f"No transfer history found but balance exists ({current_balance:.6f})")
        return self._create_pnl_result(...)
    else:
        # No balance, no transfers - nothing to report
        return self._create_empty_pnl_result(token)

# Continue to calculate realized PNL even if current_balance == 0
# (Removed early return)
```

### **Impact**
- ✅ Tracks realized PNL for sold-out positions
- ✅ Shows complete trading history
- ✅ Accurate total PNL across all activity

---

## 🐛 Bug Fix #4: Balance Mismatch Detection

### **Original Code (MISSING)**
```python
# No validation between FIFO queue and actual balance
remaining_qty = sum(p['qty'] for p in buy_queue)
unrealized_pnl = (current_price - avg_cost_basis) * current_balance
```

### **Problem**
- If `remaining_qty != current_balance`
- Could be due to:
  - Airdrops received
  - Staking/unstaking
  - Incomplete history
  - Transfers between wallets
- **SILENT FAILURE** - user unaware of issue

### **Fixed Code**
```python
# In pnl_engine.py
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

# Use actual balance for unrealized PNL (more accurate)
avg_cost_basis = safe_divide(remaining_cost, remaining_qty)
unrealized_pnl = (current_price - avg_cost_basis) * current_balance
```

### **Impact**
- ✅ Detects incomplete transaction history
- ✅ Warns user about data quality issues
- ✅ Uses actual balance (source of truth)
- ✅ Configurable tolerance

---

## 🐛 Bug Fix #5: Failed Transaction Filtering

### **Original Code (MISSING)**
```python
for tx in data.items:
    if tx.value is None or tx.value <= 0:
        continue
    # No check for tx.successful
```

### **Problem**
- Includes FAILED transactions in PNL
- Failed transactions don't affect balances
- **INCORRECT** cost basis and PNL

### **Fixed Code**
```python
# In api_client.py - fetch_native_transfers()
for tx in data.items:
    if tx.value is None or tx.value <= 0:
        continue
    
    # Skip failed transactions
    if tx.successful is False:
        continue
```

### **Impact**
- ✅ Filters out failed transactions
- ✅ Accurate transaction counts
- ✅ Correct cost basis calculations

---

## 🎯 Architectural Improvements

### **Separation of Concerns**

| Module | Responsibility |
|--------|---------------|
| `config.py` | Configuration & validation |
| `types.py` | Type definitions (TypedDict) |
| `utils.py` | Reusable utilities |
| `api_client.py` | API calls (typed) |
| `pnl_engine.py` | Core PNL logic |
| `pnl_calculator.py` | Orchestration |
| `main_v2.py` | Entry point |

### **Type Safety**

**Before:**
```python
def fetch_balances(wallet: str, chain: str) -> Dict:
    # Returns untyped dict
```

**After:**
```python
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
```

### **Error Handling**

**Before:**
```python
try:
    balances_data = fetch_balances(wallet, chain)
except Exception as e:
    print(f"Error: {e}")
```

**After:**
```python
try:
    balances_data = self.api_client.fetch_balances(wallet, chain)
except ValueError as e:
    print(f"❌ Error fetching balances: {e}")
    if self.config.verbose:
        import traceback
        traceback.print_exc()
```

---

## 📊 Warning System

### **New Warning Categories**

1. **Missing Price Data**
   ```
   Missing price data for transfer #42 on 2023-05-15, using current price $1,234.56
   ```

2. **Balance Mismatch**
   ```
   Balance mismatch: Queue=10.5, Actual=10.8, Diff=0.3 (2.86%)
   ```

3. **Sell Without Buy**
   ```
   Sell without prior buy detected (transfer #12). Possible incomplete history.
   ```

4. **No Transfer History**
   ```
   No transfer history found but balance exists (5.234567)
   ```

---

## 🚀 Performance Improvements

### **Rate Limiting**
```python
# Configurable rate limiting
if page_count % 10 == 0:
    time.sleep(self.config.rate_limit_pause)

# Handle 429 errors gracefully
if next_resp.error_code == 429:
    print(f"[RATE LIMITED] Waiting {self.config.rate_limit_retry_wait}s...")
    time.sleep(self.config.rate_limit_retry_wait)
```

### **Pagination Efficiency**
```python
# Configurable max_pages to prevent infinite loops
if page_count >= self.config.max_pages:
    if self.config.verbose:
        print(f"Reached max_pages ({max_pages})")
    break
```

---

## 📈 Testing Recommendations

### **Test Cases Added**

1. **Simple Buy & Hold**
   - Buy 100 tokens at $10
   - Current price $15
   - Expected: Unrealized PNL = $500

2. **FIFO Sells**
   - Buy 100 @ $10
   - Buy 50 @ $20
   - Sell 120 @ $25
   - Expected: Realized = $1,500, Unrealized = $150

3. **Zero Price Transfers**
   - Transfer with no USD value
   - Expected: Use current price, issue warning

4. **Balance Mismatch**
   - Queue = 10.0, Actual = 10.5
   - Expected: Warning with percentage

---

## ✅ Verification Checklist

- [x] Fixed native transfer direction logic
- [x] Added price validation with fallbacks
- [x] Handle sold-out positions correctly
- [x] Balance reconciliation with warnings
- [x] Filter failed transactions
- [x] Full type safety
- [x] Comprehensive error handling
- [x] Configurable logging (verbose mode)
- [x] Rate limiting protection
- [x] Export to JSON
- [x] Multi-chain support
- [x] Multi-wallet support

---

## 🎓 Key Learnings

1. **Always validate external data** - APIs may have missing/null values
2. **Check both sides of transactions** - from AND to addresses
3. **Balance reconciliation is critical** - FIFO queue might not match reality
4. **Type safety prevents bugs** - TypedDict catches issues at development time
5. **Warnings > Silent failures** - Alert users to data quality issues

---

**Migration Guide**: To migrate from `main.py` to `main_v2.py`:

1. Update imports to use new modules
2. Replace `Config` dictionary with `Config` dataclass
3. Use `WalletPNLCalculator` instead of manual orchestration
4. Check warnings in results for data quality issues
5. Verify PNL numbers match (they should be more accurate now!)
