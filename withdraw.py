# withdraw.py
from PyQt6 import QtWidgets, uic
import os
from PyQt6.QtWidgets import QMessageBox
from db_connection import get_cursor, commit_changes, close_connection

class WithdrawScreen(QtWidgets.QMainWindow):
    def __init__(self, user_id):
        super(WithdrawScreen, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "withdraw.ui"), self)
        
        from ui_styles import apply_style
        apply_style(self)

        self.user_id = user_id
        self.selected_account = None

        self.btnWithdraw.clicked.connect(self.withdraw_money)
        self.btnBack.clicked.connect(self.go_back)

        self.load_accounts()

        # Detect when an account is selected
        self.accountCombo.currentIndexChanged.connect(self.update_selected_account)

    # -------------------------------------------------------
    def load_accounts(self):
        """Load all account numbers of the user into the combo box."""
        cur = get_cursor()
        try:
            cur.execute("SELECT account_number, type, balance FROM account WHERE user_id = ?", (self.user_id,))
            accounts = cur.fetchall()

            if not accounts:
                QMessageBox.critical(self, "Error", "No accounts found for this user.")
                return

            self.accountCombo.clear()
            for acc_num, acc_type, balance in accounts:
                
                self.accountCombo.addItem(f"{acc_num} – {acc_type} (Bal: {balance})", acc_num)

            self.selected_account = self.accountCombo.currentData()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
        finally:
            close_connection()


    # -------------------------------------------------------
    def update_selected_account(self):
        """When user changes selection, update account number used for withdrawal."""
        self.selected_account = self.accountCombo.currentData()

    # -------------------------------------------------------
    def withdraw_money(self):
        if self.selected_account is None:
            QMessageBox.warning(self, "Error", "Please select an account first.")
            return

        amount_text = self.amountInput.text().strip()

        if not amount_text.isdigit():
            QMessageBox.warning(self, "Invalid Input", "Enter a valid amount.")
            return

        amount = float(amount_text)

        if amount <= 0:
            QMessageBox.warning(self, "Invalid Amount", "Amount must be greater than zero.")
            return

        try:
            cur = get_cursor()

            # Check balance
            cur.execute("SELECT balance FROM account WHERE account_number = ?", (self.selected_account,))
            row = cur.fetchone()

            if not row:
                QMessageBox.critical(self, "Error", "Account not found.")
                return

            current_balance = float(row[0])

            if amount > current_balance:
                QMessageBox.warning(self, "Insufficient Funds", "Not enough balance.")
                return

            # Deduct from account
            cur.execute("""
                UPDATE account
                SET balance = balance - ?
                WHERE account_number = ?
            """, (amount, self.selected_account))

            # Log transaction
            cur.execute("""
                INSERT INTO [transaction]
                (admin_id, account_number, receiver_account, amount, type, status, timestamp)
                VALUES (NULL, ?, NULL, ?, 'Withdraw', 'Approved', GETDATE())
            """, (self.selected_account, amount))

            commit_changes(auto_close=True)

            QMessageBox.information(self, "Success", f"Withdrawn Rs. {amount} successfully!")
            self.amountInput.clear()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
        finally:
            close_connection()

    # -------------------------------------------------------
    def go_back(self):
        from user_portal import UserPortal
        self.portal = UserPortal(self.user_id)
        self.portal.show()
        self.close()
