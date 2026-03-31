# Account Management System Design

## Module: `accounts.py`

### Overview
This module implements a simple account management system for a trading simulation platform. It provides functionality for account creation, fund management, share trading, portfolio valuation, and transaction tracking.

### Classes and Functions

#### 1. **Account Class**
The main class representing a user's trading account.

**Attributes:**
- `account_id` (str): Unique identifier for the account
- `balance` (float): Current cash balance in the account
- `holdings` (dict): Dictionary mapping stock symbols to quantities owned
- `transactions` (list): List of transaction records
- `initial_deposit` (float): The initial deposit amount for profit/loss calculation

**Methods:**

##### `__init__(self, account_id: str, initial_balance: float = 0.0)`
- Initializes a new account with the given ID and optional initial balance
- Validates that initial_balance is non-negative
- Sets up empty holdings and transactions list
- Records the initial deposit for profit/loss tracking

##### `deposit(self, amount: float) -> bool`
- Adds funds to the account balance
- Validates that amount is positive
- Creates a transaction record
- Returns True if successful, False otherwise

##### `withdraw(self, amount: float) -> bool`
- Removes funds from the account balance
- Validates that amount is positive and doesn't exceed available balance
- Creates a transaction record
- Returns True if successful, False otherwise

##### `buy_shares(self, symbol: str, quantity: int) -> bool`
- Records purchase of shares
- Validates that quantity is positive
- Checks if user has sufficient funds for the purchase
- Updates holdings and balance
- Creates a transaction record
- Returns True if successful, False otherwise

##### `sell_shares(self, symbol: str, quantity: int) -> bool`
- Records sale of shares
- Validates that quantity is positive
- Checks if user owns sufficient shares to sell
- Updates holdings and balance
- Creates a transaction record
- Returns True if successful, False otherwise

##### `get_portfolio_value(self) -> float`
- Calculates total portfolio value (cash + value of all holdings)
- Uses `get_share_price()` to get current prices
- Returns the total portfolio value

##### `get_holdings(self) -> dict`
- Returns a dictionary of current holdings (symbol: quantity)
- Includes only symbols with non-zero quantities

##### `get_profit_loss(self) -> float`
- Calculates profit or loss from the initial deposit
- Formula: (current portfolio value - initial deposit)
- Returns positive for profit, negative for loss

##### `get_transactions(self) -> list`
- Returns a list of all transactions in chronological order
- Each transaction includes type, amount/symbol, quantity, timestamp

##### `get_balance(self) -> float`
- Returns current cash balance

#### 2. **Transaction Class**
A data class representing a single transaction.

**Attributes:**
- `transaction_id` (str): Unique transaction identifier
- `transaction_type` (str): Type of transaction ('DEPOSIT', 'WITHDRAWAL', 'BUY', 'SELL')
- `amount` (float): Cash amount involved (for deposits/withdrawals) or price per share (for trades)
- `symbol` (str or None): Stock symbol for buy/sell transactions
- `quantity` (int or None): Number of shares for buy/sell transactions
- `timestamp` (datetime): When the transaction occurred
- `total_value` (float): Total value of the transaction

#### 3. **Helper Functions**

##### `get_share_price(symbol: str) -> float`
- Returns the current price of a share for the given symbol
- Includes a test implementation with fixed prices:
  - AAPL: $150.00
  - TSLA: $250.00
  - GOOGL: $2800.00
- For other symbols, returns a default price of $100.00
- In a real implementation, this would connect to a market data API

##### `generate_transaction_id() -> str`
- Generates a unique transaction ID using UUID and timestamp
- Format: "TXN-YYYYMMDD-UUID"

### Data Structures

#### Transaction Record Format
```python
{
    "transaction_id": "TXN-20231015-abc123",
    "type": "BUY",
    "symbol": "AAPL",
    "quantity": 10,
    "price_per_share": 150.00,
    "total_amount": 1500.00,
    "timestamp": "2023-10-15T14:30:00",
    "balance_after": 3500.00
}
```

#### Holdings Format
```python
{
    "AAPL": 50,
    "TSLA": 10,
    "GOOGL": 2
}
```

### Error Handling
- All methods validate inputs and return appropriate error indicators (False or raise exceptions)
- Insufficient funds errors for withdrawals and purchases
- Insufficient shares errors for sales
- Invalid input validation (negative amounts, zero quantities)

### Usage Example
```python
# Create account
account = Account("user123", initial_balance=10000)

# Deposit funds
account.deposit(5000)

# Buy shares
account.buy_shares("AAPL", 10)

# Check portfolio value
value = account.get_portfolio_value()

# Check profit/loss
pl = account.get_profit_loss()

# Get transaction history
transactions = account.get_transactions()
```

### Testing Considerations
- The module should be testable with mock share prices
- Edge cases: zero balance, empty portfolio, large transactions
- Concurrency considerations (though not required for this simple implementation)

### Dependencies
- Python standard library only (no external dependencies)
- Uses `datetime`, `uuid`, and `typing` modules

This design provides a complete, self-contained account management system that can be easily tested or integrated with a simple UI.