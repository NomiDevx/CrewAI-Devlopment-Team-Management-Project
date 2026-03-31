import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import uuid
import accounts

class TestGetSharePrice(unittest.TestCase):
    def test_get_share_price_known_symbols(self):
        self.assertEqual(accounts.get_share_price("AAPL"), 150.00)
        self.assertEqual(accounts.get_share_price("TSLA"), 250.00)
        self.assertEqual(accounts.get_share_price("GOOGL"), 2800.00)
        self.assertEqual(accounts.get_share_price("aapl"), 150.00)
        self.assertEqual(accounts.get_share_price("tSla"), 250.00)

    def test_get_share_price_unknown_symbol(self):
        self.assertEqual(accounts.get_share_price("UNKNOWN"), 100.00)
        self.assertEqual(accounts.get_share_price("MSFT"), 100.00)

class TestGenerateTransactionId(unittest.TestCase):
    @patch('accounts.datetime')
    def test_generate_transaction_id_format(self, mock_datetime):
        mock_now = datetime(2023, 10, 15)
        mock_datetime.now.return_value = mock_now
        with patch('uuid.uuid4') as mock_uuid:
            mock_uuid.return_value = uuid.UUID('12345678-1234-1234-1234-123456789abc')
            result = accounts.generate_transaction_id()
            self.assertTrue(result.startswith("TXN-20231015-"))
            self.assertEqual(len(result), len("TXN-20231015-12345678"))

class TestTransaction(unittest.TestCase):
    def test_transaction_initialization(self):
        with patch('accounts.generate_transaction_id') as mock_id:
            mock_id.return_value = "TXN-20231015-12345678"
            trans = accounts.Transaction(
                transaction_type="BUY",
                amount=150.0,
                symbol="AAPL",
                quantity=10,
                total_value=1500.0,
                balance_after=500.0
            )
            self.assertEqual(trans.transaction_id, "TXN-20231015-12345678")
            self.assertEqual(trans.transaction_type, "BUY")
            self.assertEqual(trans.amount, 150.0)
            self.assertEqual(trans.symbol, "AAPL")
            self.assertEqual(trans.quantity, 10)
            self.assertEqual(trans.total_value, 1500.0)
            self.assertEqual(trans.balance_after, 500.0)
            self.assertIsInstance(trans.timestamp, datetime)

    def test_transaction_to_dict_buy(self):
        with patch('accounts.generate_transaction_id') as mock_id:
            mock_id.return_value = "TXN-20231015-12345678"
            mock_timestamp = datetime(2023, 10, 15, 12, 30, 45)
            with patch('accounts.datetime') as mock_datetime:
                mock_datetime.now.return_value = mock_timestamp
                trans = accounts.Transaction(
                    transaction_type="BUY",
                    amount=150.0,
                    symbol="AAPL",
                    quantity=10,
                    total_value=1500.0,
                    balance_after=500.0
                )
                result = trans.to_dict()
                expected = {
                    "transaction_id": "TXN-20231015-12345678",
                    "type": "BUY",
                    "symbol": "AAPL",
                    "quantity": 10,
                    "price_per_share": 150.0,
                    "total_amount": 1500.0,
                    "timestamp": "2023-10-15T12:30:45",
                    "balance_after": 500.0
                }
                self.assertEqual(result, expected)

    def test_transaction_to_dict_deposit(self):
        trans = accounts.Transaction(
            transaction_type="DEPOSIT",
            amount=1000.0,
            total_value=1000.0,
            balance_after=1000.0
        )
        result = trans.to_dict()
        self.assertEqual(result["type"], "DEPOSIT")
        self.assertIsNone(result["price_per_share"])

class TestAccount(unittest.TestCase):
    def test_account_initialization(self):
        account = accounts.Account("ACC123", 1000.0)
        self.assertEqual(account.account_id, "ACC123")
        self.assertEqual(account.balance, 1000.0)
        self.assertEqual(account.holdings, {})
        self.assertEqual(account.initial_deposit, 1000.0)
        self.assertEqual(len(account.transactions), 1)
        self.assertEqual(account.transactions[0].transaction_type, "DEPOSIT")

    def test_account_initialization_zero_balance(self):
        account = accounts.Account("ACC456", 0.0)
        self.assertEqual(account.balance, 0.0)
        self.assertEqual(len(account.transactions), 0)

    def test_account_initialization_negative_balance(self):
        with self.assertRaises(ValueError):
            accounts.Account("ACC789", -100.0)

    def test_deposit_success(self):
        account = accounts.Account("ACC123", 500.0)
        result = account.deposit(200.0)
        self.assertTrue(result)
        self.assertEqual(account.balance, 700.0)
        self.assertEqual(len(account.transactions), 2)
        self.assertEqual(account.transactions[-1].transaction_type, "DEPOSIT")
        self.assertEqual(account.transactions[-1].amount, 200.0)

    def test_deposit_invalid_amount(self):
        account = accounts.Account("ACC123", 500.0)
        result = account.deposit(0.0)
        self.assertFalse(result)
        self.assertEqual(account.balance, 500.0)
        result = account.deposit(-100.0)
        self.assertFalse(result)
        self.assertEqual(account.balance, 500.0)

    def test_withdraw_success(self):
        account = accounts.Account("ACC123", 500.0)
        result = account.withdraw(200.0)
        self.assertTrue(result)
        self.assertEqual(account.balance, 300.0)
        self.assertEqual(len(account.transactions), 2)
        self.assertEqual(account.transactions[-1].transaction_type, "WITHDRAWAL")

    def test_withdraw_insufficient_funds(self):
        account = accounts.Account("ACC123", 500.0)
        result = account.withdraw(600.0)
        self.assertFalse(result)
        self.assertEqual(account.balance, 500.0)

    def test_withdraw_invalid_amount(self):
        account = accounts.Account("ACC123", 500.0)
        result = account.withdraw(0.0)
        self.assertFalse(result)
        result = account.withdraw(-100.0)
        self.assertFalse(result)
        self.assertEqual(account.balance, 500.0)

    @patch('accounts.get_share_price')
    def test_buy_shares_success(self, mock_price):
        mock_price.return_value = 150.0
        account = accounts.Account("ACC123", 2000.0)
        result = account.buy_shares("AAPL", 10)
        self.assertTrue(result)
        self.assertEqual(account.balance, 500.0)
        self.assertEqual(account.holdings, {"AAPL": 10})
        self.assertEqual(len(account.transactions), 2)
        self.assertEqual(account.transactions[-1].transaction_type, "BUY")

    @patch('accounts.get_share_price')
    def test_buy_shares_insufficient_funds(self, mock_price):
        mock_price.return_value = 150.0
        account = accounts.Account("ACC123", 1000.0)
        result = account.buy_shares("AAPL", 10)
        self.assertFalse(result)
        self.assertEqual(account.balance, 1000.0)
        self.assertEqual(account.holdings, {})

    def test_buy_shares_invalid_quantity(self):
        account = accounts.Account("ACC123", 1000.0)
        result = account.buy_shares("AAPL", 0)
        self.assertFalse(result)
        result = account.buy_shares("AAPL", -5)
        self.assertFalse(result)

    @patch('accounts.get_share_price')
    def test_sell_shares_success(self, mock_price):
        mock_price.return_value = 150.0
        account = accounts.Account("ACC123", 1000.0)
        account.buy_shares("AAPL", 10)
        initial_balance = account.balance
        result = account.sell_shares("AAPL", 5)
        self.assertTrue(result)
        self.assertEqual(account.balance, initial_balance + (150.0 * 5))
        self.assertEqual(account.holdings, {"AAPL": 5})
        self.assertEqual(account.transactions[-1].transaction_type, "SELL")

    @patch('accounts.get_share_price')
    def test_sell_shares_insufficient_holdings(self, mock_price):
        mock_price.return_value = 150.0
        account = accounts.Account("ACC123", 1000.0)
        account.buy_shares("AAPL", 5)
        result = account.sell_shares("AAPL", 10)
        self.assertFalse(result)
        result = account.sell_shares("TSLA", 1)
        self.assertFalse(result)

    def test_sell_shares_invalid_quantity(self):
        account = accounts.Account("ACC123", 1000.0)
        result = account.sell_shares("AAPL", 0)
        self.assertFalse(result)
        result = account.sell_shares("AAPL", -5)
        self.assertFalse(result)

    @patch('accounts.get_share_price')
    def test_sell_shares_removes_zero_holding(self, mock_price):
        mock_price.return_value = 150.0
        account = accounts.Account("ACC123", 1000.0)
        account.buy_shares("AAPL", 5)
        result = account.sell_shares("AAPL", 5)
        self.assertTrue(result)
        self.assertNotIn("AAPL", account.holdings)

    @patch('accounts.get_share_price')
    def test_get_portfolio_value(self, mock_price):
        mock_price.side_effect = lambda s: {"AAPL": 150.0, "TSLA": 250.0}.get(s, 100.0)
        account = accounts.Account("ACC123", 1000.0)
        account.buy_shares("AAPL", 5)
        account.buy_shares("TSLA", 2)
        portfolio_value = account.get_portfolio_value()
        expected_cash = 1000.0 - (150.0 * 5) - (250.0 * 2)
        expected_holdings = (150.0 * 5) + (250.0 * 2)
        self.assertEqual(portfolio_value, expected_cash + expected_holdings)

    def test_get_holdings(self):
        account = accounts.Account("ACC123", 1000.0)
        account.holdings = {"AAPL": 10, "TSLA": 5}
        holdings = account.get_holdings()
        self.assertEqual(holdings, {"AAPL": 10, "TSLA": 5})
        self.assertIsNot(holdings, account.holdings)

    @patch('accounts.get_share_price')
    def test_get_profit_loss(self, mock_price):
        mock_price.return_value = 160.0
        account = accounts.Account("ACC123", 1000.0)
        account.buy_shares("AAPL", 5)
        profit_loss = account.get_profit_loss()
        current_value = account.get_portfolio_value()
        expected = current_value - 1000.0
        self.assertEqual(profit_loss, expected)

    def test_get_transactions(self):
        account = accounts.Account("ACC123", 1000.0)
        account.deposit(500.0)
        transactions = account.get_transactions()
        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0]["type"], "DEPOSIT")
        self.assertEqual(transactions[1]["type"], "DEPOSIT")
        self.assertIsInstance(transactions[0], dict)

    def test_get_balance(self):
        account = accounts.Account("ACC123", 1000.0)
        self.assertEqual(account.get_balance(), 1000.0)
        account.deposit(500.0)
        self.assertEqual(account.get_balance(), 1500.0)

if __name__ == '__main__':
    unittest.main()