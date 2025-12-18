# user_portal.py
from PyQt6 import QtWidgets, uic
import os
import pyodbc
from db_connection import get_cursor, close_connection

class UserPortal(QtWidgets.QMainWindow):
    def __init__(self, user_id):
        super(UserPortal, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "user_portal.ui"), self)
        
        from ui_styles import apply_style
        apply_style(self)

        self.user_id = user_id

        # Buttons
        self.btnCreateAccount.clicked.connect(self.open_account_creator)
        self.btnWithdraw.clicked.connect(self.open_withdraw)
        self.btnDeposit.clicked.connect(self.open_deposit)
        self.btnTransfer.clicked.connect(self.open_transfer) 
        self.btnHistory.clicked.connect(self.open_history)
        self.btnShowBalance.clicked.connect(self.open_balance)
        self.btnApplyLoan.clicked.connect(self.open_loan_application)
        
        # New Pay Loan Logic
        self.btnPayLoan.clicked.connect(self.pay_loan)
        self.check_active_loans()

        self.btnBack.clicked.connect(self.go_back)

        
        self.update_button_visibility()

    def check_active_loans(self):
        """Checks if the user has any approved loans. If so, shows the Pay Loan button."""
        try:
            conn = get_cursor() # Uses the shared connection logic
            if not conn:
                 # If global connection is not established, we might need to connect manually or handle it.
                 # get_cursor checks/connects. But it returns a cursor.
                 # Let's verify get_cursor returns a cursor.
                 pass
            
            # Use execute_query helper if possible or just use the cursor directly
            # The current get_cursor returns a cursor object.
            
            cursor = get_cursor()
            
            # Check for any loan with Status 'Approved' linked to one of the user's accounts
            query = """
                SELECT COUNT(*) 
                FROM loan L
                JOIN account A ON L.account_number = A.account_number
                WHERE A.user_id = ? AND L.status = 'Approved'
            """
            cursor.execute(query, (self.user_id,))
            count = cursor.fetchval()
            
            if count and count > 0:
                self.btnPayLoan.setVisible(True)
            else:
                self.btnPayLoan.setVisible(False)
                
            # close_connection() # Typically we might not want to close it here if other parts use it, but keeping consistent with original logic which closed its own connection. 
            # However, get_cursor uses a global connection. Let's not close it aggressively to avoid breaking other things, or use the helper properly.
            # actually the original code created a NEW connection and closed it. 
            # The shared 'get_cursor' returns a global cursor. 
        except Exception as e:
            print(f"Error checking active loans: {e}")
            self.btnPayLoan.setVisible(False) # Default to hidden on error

    def pay_loan(self):
        from loan_payment import LoanPaymentScreen
        self.loan_payment_screen = LoanPaymentScreen(self.user_id)
        self.loan_payment_screen.show()
        self.close()
    
    # SHOW BUTTONS BASED ON USER ACCOUNTS
    
    def update_button_visibility(self):
        cur = get_cursor()

        # Count total accounts
        cur.execute("SELECT COUNT(*) FROM account WHERE user_id = ?", (self.user_id,))
        total_accounts = cur.fetchone()[0]

        # Count loan accounts
        cur.execute("SELECT COUNT(*) FROM account WHERE user_id = ? AND type = 'Loan'", (self.user_id,))
        loan_accounts = cur.fetchone()[0]

        close_connection()

        # Case 1: No accounts → show only Create Account
        if total_accounts == 0:
            self.btnCreateAccount.show()

            self.btnWithdraw.hide()
            self.btnDeposit.hide()
            self.btnTransfer.hide()
            self.btnHistory.hide()
            self.btnApplyLoan.hide()  # no loan account = cannot apply
            self.btnShowBalance.hide()

        else:
            # User has one or more accounts
            self.btnCreateAccount.show()
            self.btnWithdraw.show()
            self.btnDeposit.show()
            self.btnTransfer.show()
            self.btnHistory.show()
            self.btnShowBalance.show()

            # If user has a Loan Account → show Apply for Loan
            if loan_accounts > 0:
                self.btnApplyLoan.show()
            else:
                self.btnApplyLoan.hide()


    # -----------------------------------------------------
    def open_account_creator(self):
        from create_account import CreateAccountScreen
        self.screen = CreateAccountScreen(self.user_id)
        self.screen.show()
        self.hide()

    def open_withdraw(self):
        from withdraw import WithdrawScreen
        self.screen = WithdrawScreen(self.user_id)
        self.screen.show()
        self.hide()

    def open_deposit(self):
        from deposit import DepositScreen
        self.screen = DepositScreen(self.user_id)
        self.screen.show()
        self.hide()

    def open_transfer(self):
        from transfer import TransferScreen
        self.screen = TransferScreen(self.user_id)
        self.screen.show()
        self.hide()

    def open_history(self):
        from transaction_history import TransactionHistoryScreen
        self.screen = TransactionHistoryScreen(self.user_id)
        self.screen.show()
        self.hide()

   
    # OPEN APPLY LOAN PAGE
    
    def open_loan_application(self):
        from apply_loan import ApplyLoanScreen
        self.screen = ApplyLoanScreen(self.user_id)
        self.screen.show()
        self.hide()
    
    def open_balance(self):
        import view_balance
        self.screen = view_balance.ViewBalanceScreen(self.user_id)
        self.screen.show()
        self.hide()

    
    def go_back(self):
        from login import LoginOptions
        self.screen = LoginOptions()
        self.screen.show()
        self.hide()