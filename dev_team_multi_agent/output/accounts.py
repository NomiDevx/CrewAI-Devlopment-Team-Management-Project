import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union


def get_share_price(symbol: str) -> float:
    """Returns the current price of a share for the given symbol.
    Test implementation with fixed prices for AAPL, TSLA, GOOGL.
    """
    prices = {
        "AAPL": 150.00,
        "TSLA": 250.00,
        "GOOGL": 2800.00,
    }
    return prices.get(symbol.upper(), 100.00)


def generate_transaction_id() -> str:
    """Generates a unique transaction ID."""
    date_str = datetime.now().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())[:8]
    return f"TXN-{date_str}-{unique_id}"


class Transaction:
    """Represents a single transaction in the account."""

    def __init__(
        self,
        transaction_type: str,
        amount: float,
        symbol: Optional[str] = None,
        quantity: Optional[int] = None,
        total_value: float = 0.0,
        balance_after: float = 0.0,
    ):
        self.transaction_id = generate_transaction_id()
        self.transaction_type = transaction_type
        self.amount = amount  # cash amount or price per share
        self.symbol = symbol
        self.quantity = quantity
        self.timestamp = datetime.now()
        self.total_value = total_value
        self.balance_after = balance_after

    def to_dict(self) -> dict:
        """Returns transaction as a dictionary."""
        return {
            "transaction_id": self.transaction_id,
            "type": self.transaction_type,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "price_per_share": self.amount if self.transaction_type in ["BUY", "SELL"] else None,
            "total_amount": self.total_value,
            "timestamp": self.timestamp.isoformat(),
            "balance_after": self.balance_after,
        }


class Account:
    """Represents a user's trading account."""

    def __init__(self, account_id: str, initial_balance: float = 0.0):
        """Initializes a new account.
        
        Args:
            account_id: Unique identifier for the account
            initial_balance: Starting cash balance (must be non-negative)
            
        Raises:
            ValueError: If initial_balance is negative
        """
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative")
        
        self.account_id = account_id
        self.balance = initial_balance
        self.holdings: Dict[str, int] = {}  # symbol -> quantity
        self.transactions: List[Transaction] = []
        self.initial_deposit = initial_balance
        
        # Record initial deposit as a transaction if positive
        if initial_balance > 0:
            transaction = Transaction(
                transaction_type="DEPOSIT",
                amount=initial_balance,
                total_value=initial_balance,
                balance_after=initial_balance,
            )
            self.transactions.append(transaction)

    def deposit(self, amount: float) -> bool:
        """Deposits funds into the account.
        
        Args:
            amount: Amount to deposit (must be positive)
            
        Returns:
            True if successful, False otherwise
        """
        if amount <= 0:
            return False
        
        self.balance += amount
        transaction = Transaction(
            transaction_type="DEPOSIT",
            amount=amount,
            total_value=amount,
            balance_after=self.balance,
        )
        self.transactions.append(transaction)
        return True

    def withdraw(self, amount: float) -> bool:
        """Withdraws funds from the account.
        
        Args:
            amount: Amount to withdraw (must be positive)
            
        Returns:
            True if successful, False otherwise
        """
        if amount <= 0:
            return False
        
        if amount > self.balance:
            return False
        
        self.balance -= amount
        transaction = Transaction(
            transaction_type="WITHDRAWAL",
            amount=amount,
            total_value=amount,
            balance_after=self.balance,
        )
        self.transactions.append(transaction)
        return True

    def buy_shares(self, symbol: str, quantity: int) -> bool:
        """Buys shares of a stock.
        
        Args:
            symbol: Stock symbol to buy
            quantity: Number of shares to buy (must be positive)
            
        Returns:
            True if successful, False otherwise
        """
        if quantity <= 0:
            return False
        
        price_per_share = get_share_price(symbol)
        total_cost = price_per_share * quantity
        
        if total_cost > self.balance:
            return False
        
        # Update balance
        self.balance -= total_cost
        
        # Update holdings
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        
        # Record transaction
        transaction = Transaction(
            transaction_type="BUY",
            amount=price_per_share,
            symbol=symbol,
            quantity=quantity,
            total_value=total_cost,
            balance_after=self.balance,
        )
        self.transactions.append(transaction)
        return True

    def sell_shares(self, symbol: str, quantity: int) -> bool:
        """Sells shares of a stock.
        
        Args:
            symbol: Stock symbol to sell
            quantity: Number of shares to sell (must be positive)
            
        Returns:
            True if successful, False otherwise
        """
        if quantity <= 0:
            return False
        
        current_quantity = self.holdings.get(symbol, 0)
        if current_quantity < quantity:
            return False
        
        price_per_share = get_share_price(symbol)
        total_value = price_per_share * quantity
        
        # Update balance
        self.balance += total_value
        
        # Update holdings
        self.holdings[symbol] = current_quantity - quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
        
        # Record transaction
        transaction = Transaction(
            transaction_type="SELL",
            amount=price_per_share,
            symbol=symbol,
            quantity=quantity,
            total_value=total_value,
            balance_after=self.balance,
        )
        self.transactions.append(transaction)
        return True

    def get_portfolio_value(self) -> float:
        """Calculates total portfolio value (cash + holdings).
        
        Returns:
            Total portfolio value
        """
        holdings_value = 0.0
        for symbol, quantity in self.holdings.items():
            price = get_share_price(symbol)
            holdings_value += price * quantity
        
        return self.balance + holdings_value

    def get_holdings(self) -> Dict[str, int]:
        """Returns current holdings.
        
        Returns:
            Dictionary of symbol -> quantity (only non-zero holdings)
        """
        return self.holdings.copy()

    def get_profit_loss(self) -> float:
        """Calculates profit or loss from initial deposit.
        
        Returns:
            Profit (positive) or loss (negative) amount
        """
        current_value = self.get_portfolio_value()
        return current_value - self.initial_deposit

    def get_transactions(self) -> List[dict]:
        """Returns all transactions in chronological order.
        
        Returns:
            List of transaction dictionaries
        """
        return [t.to_dict() for t in self.transactions]

    def get_balance(self) -> float:
        """Returns current cash balance.
        
        Returns:
            Current balance
        """
        return self.balance