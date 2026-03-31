import gradio as gr
from accounts import Account

# Global account instance (single user)
account = None

def create_account(account_id, initial_balance):
    global account
    try:
        initial_balance = float(initial_balance)
        if initial_balance < 0:
            return "Error: Initial balance cannot be negative.", "", "", "", ""
        account = Account(account_id, initial_balance)
        return f"Account '{account_id}' created with ${initial_balance:.2f} initial deposit.", "", "", "", ""
    except Exception as e:
        return f"Error creating account: {str(e)}", "", "", "", ""

def deposit_funds(amount):
    global account
    if account is None:
        return "Please create an account first.", "", "", "", ""
    try:
        amount = float(amount)
        if account.deposit(amount):
            return f"Deposited ${amount:.2f} successfully.", "", "", "", ""
        else:
            return "Deposit failed: amount must be positive.", "", "", "", ""
    except Exception as e:
        return f"Error: {str(e)}", "", "", "", ""

def withdraw_funds(amount):
    global account
    if account is None:
        return "Please create an account first.", "", "", "", ""
    try:
        amount = float(amount)
        if account.withdraw(amount):
            return f"Withdrew ${amount:.2f} successfully.", "", "", "", ""
        else:
            return "Withdrawal failed: insufficient funds or invalid amount.", "", "", "", ""
    except Exception as e:
        return f"Error: {str(e)}", "", "", "", ""

def buy_shares(symbol, quantity):
    global account
    if account is None:
        return "Please create an account first.", "", "", "", ""
    try:
        quantity = int(quantity)
        if account.buy_shares(symbol, quantity):
            return f"Bought {quantity} shares of {symbol} successfully.", "", "", "", ""
        else:
            return "Buy failed: insufficient funds, invalid quantity, or invalid symbol.", "", "", "", ""
    except Exception as e:
        return f"Error: {str(e)}", "", "", "", ""

def sell_shares(symbol, quantity):
    global account
    if account is None:
        return "Please create an account first.", "", "", "", ""
    try:
        quantity = int(quantity)
        if account.sell_shares(symbol, quantity):
            return f"Sold {quantity} shares of {symbol} successfully.", "", "", "", ""
        else:
            return "Sell failed: insufficient shares, invalid quantity, or invalid symbol.", "", "", "", ""
    except Exception as e:
        return f"Error: {str(e)}", "", "", "", ""

def update_display():
    global account
    if account is None:
        return "No account created yet.", "N/A", "N/A", "No holdings.", "No transactions."
    try:
        balance = account.get_balance()
        portfolio_value = account.get_portfolio_value()
        profit_loss = account.get_profit_loss()
        holdings = account.get_holdings()
        transactions = account.get_transactions()
        
        balance_str = f"${balance:.2f}"
        portfolio_str = f"${portfolio_value:.2f}"
        profit_loss_str = f"${profit_loss:.2f}"
        
        holdings_str = ""
        if holdings:
            for symbol, qty in holdings.items():
                holdings_str += f"{symbol}: {qty} shares\n"
        else:
            holdings_str = "No holdings."
        
        transactions_str = ""
        if transactions:
            for t in transactions[-10:]:  # Show last 10 transactions
                trans_type = t['type']
                symbol = t['symbol'] or ''
                qty = t['quantity'] or ''
                total = t['total_amount']
                timestamp = t['timestamp'][:19]
                if trans_type in ['BUY', 'SELL']:
                    transactions_str += f"{timestamp} {trans_type} {symbol} {qty} shares @ ${t['price_per_share']:.2f} total ${total:.2f}\n"
                else:
                    transactions_str += f"{timestamp} {trans_type} ${total:.2f}\n"
        else:
            transactions_str = "No transactions."
        
        return balance_str, portfolio_str, profit_loss_str, holdings_str.strip(), transactions_str.strip()
    except Exception as e:
        return f"Error: {str(e)}", "N/A", "N/A", "N/A", "N/A"

def perform_action(action, *args):
    result = ""
    if action == "create":
        result = create_account(*args)
    elif action == "deposit":
        result = deposit_funds(*args)
    elif action == "withdraw":
        result = withdraw_funds(*args)
    elif action == "buy":
        result = buy_shares(*args)
    elif action == "sell":
        result = sell_shares(*args)
    
    display_data = update_display()
    if isinstance(result, tuple):
        return result[0], *display_data
    else:
        return result, *display_data

with gr.Blocks(title="Trading Account Demo") as demo:
    gr.Markdown("# Trading Account Management System")
    gr.Markdown("Single-user demo. Create an account first.")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Account Actions")
            account_id = gr.Textbox(label="Account ID", placeholder="e.g., user123")
            initial_balance = gr.Number(label="Initial Deposit", value=1000.0)
            create_btn = gr.Button("Create Account")
            
            deposit_amt = gr.Number(label="Deposit Amount", value=100.0)
            deposit_btn = gr.Button("Deposit Funds")
            
            withdraw_amt = gr.Number(label="Withdraw Amount", value=50.0)
            withdraw_btn = gr.Button("Withdraw Funds")
            
            buy_symbol = gr.Textbox(label="Buy Symbol", placeholder="AAPL, TSLA, GOOGL")
            buy_qty = gr.Number(label="Buy Quantity", value=1, precision=0)
            buy_btn = gr.Button("Buy Shares")
            
            sell_symbol = gr.Textbox(label="Sell Symbol", placeholder="AAPL, TSLA, GOOGL")
            sell_qty = gr.Number(label="Sell Quantity", value=1, precision=0)
            sell_btn = gr.Button("Sell Shares")
            
            refresh_btn = gr.Button("Refresh Display")
        
        with gr.Column(scale=1):
            gr.Markdown("### Account Status")
            status_msg = gr.Textbox(label="Action Result", interactive=False)
            cash_balance = gr.Textbox(label="Cash Balance", interactive=False)
            portfolio_value = gr.Textbox(label="Portfolio Value", interactive=False)
            profit_loss = gr.Textbox(label="Profit/Loss", interactive=False)
            holdings = gr.Textbox(label="Current Holdings", interactive=False, lines=4)
            transactions = gr.Textbox(label="Recent Transactions", interactive=False, lines=8)
    
    create_btn.click(
        perform_action,
        inputs=[gr.State("create"), account_id, initial_balance],
        outputs=[status_msg, cash_balance, portfolio_value, profit_loss, holdings, transactions]
    )
    deposit_btn.click(
        perform_action,
        inputs=[gr.State("deposit"), deposit_amt],
        outputs=[status_msg, cash_balance, portfolio_value, profit_loss, holdings, transactions]
    )
    withdraw_btn.click(
        perform_action,
        inputs=[gr.State("withdraw"), withdraw_amt],
        outputs=[status_msg, cash_balance, portfolio_value, profit_loss, holdings, transactions]
    )
    buy_btn.click(
        perform_action,
        inputs=[gr.State("buy"), buy_symbol, buy_qty],
        outputs=[status_msg, cash_balance, portfolio_value, profit_loss, holdings, transactions]
    )
    sell_btn.click(
        perform_action,
        inputs=[gr.State("sell"), sell_symbol, sell_qty],
        outputs=[status_msg, cash_balance, portfolio_value, profit_loss, holdings, transactions]
    )
    refresh_btn.click(
        update_display,
        inputs=[],
        outputs=[cash_balance, portfolio_value, profit_loss, holdings, transactions]
    )

if __name__ == "__main__":
    demo.launch()