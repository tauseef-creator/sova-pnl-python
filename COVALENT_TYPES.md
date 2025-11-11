# Covalent API Type Reference

This document provides a comprehensive guide to the types used in the Covalent API.

## Core Response Type

All API methods return a `Response[T]` generic type:

```python
from covalent.services.util.api_helper import Response

class Response[T]:
    data: Optional[T]           # The actual response data (type depends on the endpoint)
    error: bool                 # True if an error occurred
    error_code: Optional[int]   # HTTP error code if error occurred
    error_message: Optional[str] # Error message if error occurred
```

## Balance Service Types

### get_token_balances_for_wallet_address()

**Returns:** `Response[BalancesResponse]`

```python
from covalent.services.balance_service import BalancesResponse, BalanceItem

class BalancesResponse:
    address: str                    # The requested address
    chain_id: int                   # The chain ID (e.g., 1 for Ethereum mainnet)
    chain_name: str                 # The chain name (e.g., "eth-mainnet")
    quote_currency: str             # Quote currency (e.g., "USD")
    updated_at: datetime            # When the response was generated
    items: List[BalanceItem]        # List of token balances

class BalanceItem:
    contract_decimals: Optional[int]            # Token decimals (e.g., 18 for most ERC20)
    contract_name: Optional[str]                # Token name (e.g., "USD Coin")
    contract_ticker_symbol: Optional[str]       # Token symbol (e.g., "USDC")
    contract_address: Optional[str]             # Token contract address
    contract_display_name: Optional[str]        # Display-friendly name
    supports_erc: Optional[List[str]]           # Supported ERCs (e.g., ["ERC20"])
    logo_url: Optional[str]                     # Token logo URL
    logo_urls: Optional[LogoUrls]               # Multiple logo URLs
    last_transferred_at: Optional[datetime]     # Last transfer timestamp
    native_token: Optional[bool]                # True for native gas tokens (ETH, MATIC, etc.)
    type: Optional[str]                         # "cryptocurrency", "stablecoin", "nft", or "dust"
    is_spam: Optional[bool]                     # True if suspected spam token
    balance: Optional[int]                      # Raw balance (use contract_decimals to format)
    balance_24h: Optional[int]                  # Balance 24h ago
    quote_rate: Optional[float]                 # Current price in quote currency
    quote_rate_24h: Optional[float]             # Price 24h ago
    quote: Optional[float]                      # Balance value in quote currency
    quote_24h: Optional[float]                  # Balance value 24h ago in quote currency
    pretty_quote: Optional[str]                 # Formatted quote string (e.g., "$1,234.56")
    pretty_quote_24h: Optional[str]             # Formatted 24h quote string
    protocol_metadata: Optional[ProtocolMetadata]  # Protocol info (for DeFi positions)
    nft_data: Optional[List[BalanceNftData]]    # NFT-specific data
```

### get_historical_portfolio_for_wallet_address()

**Returns:** `Response[PortfolioResponse]`

```python
class PortfolioResponse:
    address: str                    # The requested address
    updated_at: datetime            # When the response was generated
    quote_currency: str             # Quote currency
    chain_id: int                   # Chain ID
    chain_name: str                 # Chain name
    items: List[PortfolioItem]      # Portfolio items

class PortfolioItem:
    contract_address: Optional[str]
    contract_decimals: Optional[int]
    contract_name: Optional[str]
    contract_ticker_symbol: Optional[str]
    logo_url: Optional[str]
    holdings: Optional[List[HoldingItem]]

class HoldingItem:
    quote_rate: Optional[float]     # Exchange rate
    timestamp: Optional[datetime]   # Data timestamp
    close: Optional[OhlcItem]       # Closing values
    high: Optional[OhlcItem]        # High values
    low: Optional[OhlcItem]         # Low values
    open: Optional[OhlcItem]        # Opening values
```

### get_erc20_transfers_for_wallet_address_by_page()

**Returns:** `Response[Erc20TransfersResponse]`

```python
class Erc20TransfersResponse:
    address: str
    updated_at: datetime
    quote_currency: str
    chain_id: int
    chain_name: str
    items: List[BlockTransactionWithContractTransfers]
    pagination: Optional[Pagination]

class BlockTransactionWithContractTransfers:
    block_signed_at: Optional[datetime]     # Block timestamp
    block_height: Optional[int]             # Block number
    block_hash: Optional[str]               # Block hash
    tx_hash: Optional[str]                  # Transaction hash
    tx_offset: Optional[int]                # Position in block
    successful: Optional[bool]              # Transaction success status
    from_address: Optional[str]             # Sender address
    from_address_label: Optional[str]       # Sender label
    to_address: Optional[str]               # Receiver address
    to_address_label: Optional[str]         # Receiver label
    value: Optional[int]                    # Transaction value in wei
    value_quote: Optional[float]            # Value in quote currency
    gas_spent: Optional[int]                # Gas used
    gas_price: Optional[int]                # Gas price in wei
    fees_paid: Optional[int]                # Total fees in wei
    gas_quote: Optional[float]              # Gas cost in quote currency
    transfers: Optional[List[TokenTransferItem]]  # Token transfers in this tx

class TokenTransferItem:
    block_signed_at: Optional[datetime]
    tx_hash: Optional[str]
    from_address: Optional[str]
    to_address: Optional[str]
    contract_decimals: Optional[int]
    contract_name: Optional[str]
    contract_ticker_symbol: Optional[str]
    contract_address: Optional[str]
    logo_url: Optional[str]
    transfer_type: Optional[str]            # "transfer-in" or "transfer-out"
    delta: Optional[int]                    # Change in balance (raw)
    balance: Optional[int]                  # Balance after transfer (raw)
    quote_rate: Optional[float]             # Price at time of transfer
    delta_quote: Optional[float]            # Value of transfer
    balance_quote: Optional[float]          # Balance value after transfer
```

### get_token_holders_v2_for_token_address_by_page()

**Returns:** `Response[TokenHoldersResponse]`

```python
class TokenHoldersResponse:
    updated_at: datetime
    chain_id: int
    chain_name: str
    items: List[TokenHolder]
    pagination: Optional[Pagination]

class TokenHolder:
    contract_decimals: Optional[int]
    contract_name: Optional[str]
    contract_ticker_symbol: Optional[str]
    contract_address: Optional[str]
    supports_erc: Optional[List[str]]
    logo_url: Optional[str]
    address: Optional[str]                  # Holder's address
    balance: Optional[int]                  # Holder's balance (raw)
    total_supply: Optional[int]             # Total token supply
    block_height: Optional[int]             # Block height of data
```

### get_historical_token_balances_for_wallet_address()

**Returns:** `Response[HistoricalBalancesResponse]`

```python
class HistoricalBalancesResponse:
    address: str
    updated_at: datetime
    quote_currency: str
    chain_id: int
    chain_name: str
    items: List[HistoricalBalanceItem]

class HistoricalBalanceItem:
    # Similar to BalanceItem but for historical data
    contract_decimals: Optional[int]
    contract_name: Optional[str]
    contract_ticker_symbol: Optional[str]
    contract_address: Optional[str]
    block_height: Optional[int]             # Block height of the historical data
    last_transferred_block_height: Optional[int]
    balance: Optional[int]
    quote_rate: Optional[float]
    quote: Optional[float]
    # ... (other fields similar to BalanceItem)
```

### get_native_token_balance()

**Returns:** `Response[TokenBalanceNativeResponse]`

```python
class TokenBalanceNativeResponse:
    address: str
    updated_at: datetime
    quote_currency: str
    chain_id: int
    chain_name: str
    items: List[NativeBalanceItem]

class NativeBalanceItem:
    contract_decimals: Optional[int]
    contract_name: Optional[str]            # e.g., "Ether"
    contract_ticker_symbol: Optional[str]   # e.g., "ETH"
    contract_address: Optional[str]         # Usually "0xeeee..." for native tokens
    balance: Optional[int]                  # Balance in wei
    quote_rate: Optional[float]             # Current price
    quote: Optional[float]                  # Balance value in quote currency
    pretty_quote: Optional[str]             # Formatted quote string
```

## Common Helper Types

### Pagination

```python
class Pagination:
    has_more: Optional[bool]        # True if more pages available
    page_number: Optional[int]      # Current page number (0-indexed)
    page_size: Optional[int]        # Items per page
    total_count: Optional[int]      # Total items across all pages
```

### LogoUrls

```python
class LogoUrls:
    token_logo_url: Optional[str]
    protocol_logo_url: Optional[str]
    chain_logo_url: Optional[str]
```

### ContractMetadata

```python
class ContractMetadata:
    contract_decimals: Optional[int]
    contract_name: Optional[str]
    contract_ticker_symbol: Optional[str]
    contract_address: Optional[str]
    supports_erc: Optional[List[str]]
    logo_url: Optional[str]
```

## Usage Examples

### Example 1: Get Token Balances with Types

```python
from covalent import CovalentClient
from covalent.services.balance_service import BalancesResponse, BalanceItem
from covalent.services.util.api_helper import Response

def get_wallet_balances(wallet: str) -> None:
    client: CovalentClient = CovalentClient("your_api_key")
    
    response: Response[BalancesResponse] = client.balance_service.get_token_balances_for_wallet_address(
        "eth-mainnet",
        wallet
    )
    
    if not response.error:
        data: BalancesResponse = response.data
        
        # Access properties with full type support
        print(f"Wallet: {data.address}")
        print(f"Chain: {data.chain_name} (ID: {data.chain_id})")
        
        # Iterate through balances
        item: BalanceItem
        for item in data.items:
            if item.balance and item.balance > 0:
                # Calculate human-readable balance
                decimals: int = item.contract_decimals or 18
                readable_balance: float = item.balance / (10 ** decimals)
                
                print(f"{item.contract_ticker_symbol}: {readable_balance:.6f}")
                print(f"  Value: {item.pretty_quote}")
    else:
        print(f"Error: {response.error_message}")
```

### Example 2: Get Transaction History

```python
from covalent.services.balance_service import (
    Erc20TransfersResponse,
    BlockTransactionWithContractTransfers,
    TokenTransferItem
)

def get_transfer_history(wallet: str) -> None:
    client: CovalentClient = CovalentClient("your_api_key")
    
    response: Response[Erc20TransfersResponse] = (
        client.balance_service.get_erc20_transfers_for_wallet_address_by_page(
            "eth-mainnet",
            wallet,
            page_size=10
        )
    )
    
    if not response.error:
        data: Erc20TransfersResponse = response.data
        
        tx: BlockTransactionWithContractTransfers
        for tx in data.items:
            print(f"\nTx: {tx.tx_hash}")
            print(f"Block: {tx.block_height}")
            print(f"Time: {tx.block_signed_at}")
            print(f"Success: {tx.successful}")
            
            if tx.transfers:
                transfer: TokenTransferItem
                for transfer in tx.transfers:
                    print(f"  {transfer.transfer_type}: {transfer.contract_ticker_symbol}")
                    print(f"  Amount: {transfer.delta}")
```

### Example 3: Calculate Portfolio Value

```python
def calculate_portfolio_value(wallet: str) -> float:
    client: CovalentClient = CovalentClient("your_api_key")
    
    response: Response[BalancesResponse] = client.balance_service.get_token_balances_for_wallet_address(
        "eth-mainnet",
        wallet,
        quote_currency="USD",
        no_spam=True  # Filter out spam tokens
    )
    
    if response.error:
        print(f"Error: {response.error_message}")
        return 0.0
    
    data: BalancesResponse = response.data
    total_value: float = 0.0
    
    item: BalanceItem
    for item in data.items:
        # Only count tokens with a quote value
        if item.quote and not item.is_spam:
            total_value += item.quote
    
    return total_value
```

## Important Notes

1. **Raw Balances**: Most balance values are returned as raw integers. Use `contract_decimals` to convert:
   ```python
   human_readable = balance / (10 ** contract_decimals)
   ```

2. **Error Handling**: Always check `response.error` before accessing `response.data`:
   ```python
   if not response.error:
       data = response.data  # Safe to access
   else:
       print(response.error_message)
   ```

3. **Optional Fields**: Most fields are `Optional`, so check for `None`:
   ```python
   if item.quote:
       print(f"Value: ${item.quote}")
   ```

4. **Pagination**: Use `pagination.has_more` to check for more data:
   ```python
   if data.pagination and data.pagination.has_more:
       # Fetch next page
   ```

## Additional Resources

- **Official Covalent API Docs**: https://www.covalenthq.com/docs/api/
- **Supported Chains**: Use `Chains` enum or string like "eth-mainnet", "matic-mainnet", etc.
- **Quote Currencies**: USD, CAD, EUR, SGD, INR, JPY, VND, CNY, KRW, RUB, TRY, NGN, ARS, AUD, CHF, GBP
