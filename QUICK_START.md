# Quick Start Guide - PNL Calculator v2

## 🚀 Get Started in 5 Minutes

### Step 1: Get Your Covalent API Key (FREE)

1. Go to https://www.covalenthq.com/
2. Click "Get API Key" (free tier available)
3. Copy your API key (starts with `cqt_...`)

### Step 2: Configure `main_v2.py`

Open `main_v2.py` and edit these lines:

```python
config = Config(
    api_key="cqt_YOUR_KEY_HERE",  # <-- Paste your API key
    wallets=[
        "0xYOUR_WALLET_HERE"       # <-- Paste your wallet address
    ],
    chains=["eth-mainnet"],        # <-- Choose your blockchain
    verbose=True,                   # <-- Keep True to see details
)
```

### Step 3: Run It!

```bash
python main_v2.py
```

That's it! You'll see a detailed PNL report in your terminal.

---

## 📋 Example Configuration Options

### Single Wallet, Single Chain
```python
config = Config(
    api_key="cqt_rQRKdJKWqr888G3hK6bHcHXFGwf3",
    wallets=["0xf29C6705F188526E0029A92EE6bc21Ebc750b675"],
    chains=["eth-mainnet"],
    verbose=True
)
```

### Multiple Wallets, Single Chain
```python
config = Config(
    api_key="cqt_...",
    wallets=[
        "0xWallet1...",
        "0xWallet2...",
        "0xWallet3..."
    ],
    chains=["eth-mainnet"],
    verbose=True
)
```

### Single Wallet, Multiple Chains
```python
config = Config(
    api_key="cqt_...",
    wallets=["0xYourWallet..."],
    chains=[
        "eth-mainnet",
        "matic-mainnet",    # Polygon
        "bsc-mainnet",      # Binance Smart Chain
        "arbitrum-mainnet"  # Arbitrum
    ],
    verbose=True
)
```

### Production Mode (Less Verbose)
```python
config = Config(
    api_key="cqt_...",
    wallets=["0x..."],
    chains=["eth-mainnet"],
    verbose=False,  # <-- Only show summary
    max_pages=100    # <-- Limit API calls
)
```

---

## 🎯 Understanding Your Results

### Sample Output Explained

```
→ ETH      | Balance:    5.234567 | Price: $3,250.00
  Fetched 234 transfers
  ├─ Cost Basis: $2,890.50    👈 Your average buy price
  ├─ Invested:   $15,234.00   👈 Total money you put in
  ├─ Value Now:  $17,012.34   👈 Current value of holdings
  ├─ Realized:   $1,450.00    👈 Profit from sells
  ├─ Unrealized: $1,882.34    👈 Profit if you sold now
  ├─ Total PNL:  $3,332.34    👈 Total profit/loss
  └─ Positions:  12 opened, 7 closed
```

### Key Metrics

| Metric | What It Means |
|--------|---------------|
| **Cost Basis** | Average price you paid per token |
| **Invested** | Total USD spent (including gas) |
| **Value Now** | What your holdings are worth today |
| **Realized PNL** | Profit/loss from tokens you sold |
| **Unrealized PNL** | Profit/loss if you sold today |
| **Total PNL** | Realized + Unrealized |
| **ROI %** | Return on investment percentage |

---

## ⚠️ Common Warnings & What They Mean

### 1. Missing Price Data
```
Missing price data for transfer #42 on 2023-05-15, using current price $1,234.56
```
**Meaning**: Covalent doesn't have historical price for that date
**Impact**: Calculator uses current price as fallback
**Action**: None needed - this is informational

### 2. Balance Mismatch
```
Balance mismatch: Queue=10.5, Actual=10.8, Diff=0.3 (2.86%)
```
**Meaning**: Incomplete transaction history OR airdrops/staking events
**Impact**: PNL uses actual balance (accurate)
**Action**: If difference is large (>5%), check if wallet received airdrops

### 3. Sell Without Buy
```
Sell without prior buy detected (transfer #12). Possible incomplete history.
```
**Meaning**: Wallet sold tokens but no buy transaction found
**Impact**: May underestimate realized PNL
**Action**: Check if wallet was funded before Covalent started indexing

### 4. No Transfer History
```
No transfer history found but balance exists (5.234567)
```
**Meaning**: Tokens appeared without transfers (airdrop, migration, etc.)
**Impact**: Cost basis is $0, full value counted as unrealized PNL
**Action**: This is correct for airdrops

---

## 🔧 Troubleshooting

### "Invalid API key"
**Problem**: API key not recognized
**Solution**: 
1. Check you copied the full key (starts with `cqt_`)
2. Get a new key from https://www.covalenthq.com/

### "Error fetching balances"
**Problem**: API request failed
**Solution**:
1. Check internet connection
2. Verify wallet address format (starts with `0x`, 42 characters)
3. Check if chain name is correct (e.g., `eth-mainnet`)

### "Rate limited (429)"
**Problem**: Too many API requests
**Solution**:
```python
config = Config(
    api_key="...",
    max_pages=100,  # <-- Reduce this
    # ...
)
```

### Results seem incorrect
**Problem**: PNL numbers don't match expectations
**Solution**:
1. Set `verbose=True` to see detailed breakdown
2. Check warnings - they often explain discrepancies
3. Verify the wallet address is correct
4. Remember: This uses FIFO accounting (First In, First Out)

---

## 📊 Export Results to JSON

Uncomment this line in `main_v2.py`:

```python
# Optional: Export results to JSON
if results:
    export_to_json(results, "pnl_results.json")  # <-- Uncomment this
```

This creates `pnl_results.json` with all your data for:
- Tax preparation
- Record keeping
- Further analysis
- Importing to spreadsheet

---

## 🎓 Best Practices

### 1. Start Small
```python
# Test with one wallet first
wallets=["0xYourMainWallet"]
```

### 2. Use Verbose Mode Initially
```python
verbose=True  # See what's happening
```

### 3. Export Your Data
```python
# Keep records for taxes
export_to_json(results, f"pnl_{datetime.now().strftime('%Y%m%d')}.json")
```

### 4. Run Regularly
- Weekly: Track your portfolio
- Monthly: Generate reports
- Quarterly: Tax planning
- Yearly: Tax filing

### 5. Secure Your API Key
```python
# Don't commit to GitHub!
# Use environment variables:
export COVALENT_API_KEY="cqt_..."
config = Config.from_env()
```

---

## 🆚 Difference from Original

| Feature | Original `main.py` | New `main_v2.py` |
|---------|-------------------|------------------|
| Type Safety | ❌ None | ✅ Full typing |
| Price Validation | ❌ None | ✅ With fallbacks |
| Balance Check | ❌ None | ✅ Reconciliation |
| Warnings | ❌ Silent | ✅ Detailed |
| Failed TX Filter | ❌ No | ✅ Yes |
| Transfer Logic | ❌ Buggy | ✅ Fixed |
| Architecture | ❌ Single file | ✅ Modular |
| Error Handling | ❌ Basic | ✅ Comprehensive |

---

## 🚀 Next Steps

1. ✅ Run your first PNL calculation
2. 📊 Review the results
3. ⚠️ Check warnings and understand them
4. 💾 Export to JSON for records
5. 🔁 Set up regular runs
6. 📈 Track your portfolio over time

---

## 💡 Pro Tips

### Calculate Multiple Time Periods
Save results with dates:
```bash
python main_v2.py  # Today
mv pnl_results.json pnl_2024_11_12.json

# Compare monthly:
# pnl_2024_10_12.json vs pnl_2024_11_12.json
```

### Combine with Excel/Google Sheets
Import JSON into spreadsheet for charts and analysis

### Use for Tax Reporting
Realized PNL = Your taxable gains/losses

---

Need help? Check:
- `README_V2.md` - Full documentation
- `FIXES_APPLIED.md` - Technical details
- Covalent Docs - https://www.covalenthq.com/docs/

**Happy calculating! 🎉**
