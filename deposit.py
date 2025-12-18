# deposit.py
from PyQt6 import QtWidgets, uic
import os
from PyQt6.QtWidgets import QMessageBox
from db_connection import get_cursor, commit_changes, close_connection

class DepositScreen(QtWidgets.QMainWindow):
    def __init__(self, user_id):
        super(DepositScreen, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "deposit.ui"), self)

        from ui_styles import apply_style
        apply_style(self)

        self.user_id = user_id
        self.selected_account = None

        self.btnDeposit.clicked.connect(self.deposit_money)
        self.btnBack.clicked.connect(self.go_back)

        self.load_accounts()

        # update account on dropdown change
        self.accountCombo.currentIndexChanged.connect(self.update_selected_account)

    # ------------------------------------------
    def load_accounts(self):
        cur = get_cursor()
        try:
            cur.execute("SELECT account_number, type, balance FROM account WHERE user_id = ?", (self.user_id,))
            accounts = cur.fetchall()

            if not accounts:
                QMessageBox.critical(self, "Error", "No accounts found for this user.")
                return

            self.accountCombo.clear()
            for acc_num, acc_type, balance in accounts:
                # Display “1001 – Normal (Bal: 5000.0)”
                self.accountCombo.addItem(f"{acc_num} – {acc_type} (Bal: {balance})", acc_num)

            # set default selected account
            self.selected_account = self.accountCombo.currentData()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
        finally:
            close_connection()

    # ------------------------------------------
    def update_selected_account(self):
        self.selected_account = self.accountCombo.currentData()

    # ------------------------------------------
    def deposit_money(self):
        if self.selected_account is None:
            QMessageBox.warning(self, "Error", "Select an account first.")
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

            # Update account balance
            cur.execute("""
                UPDATE account
                SET balance = balance + ?
                WHERE account_number = ?
            """, (amount, self.selected_account))

            # Insert transaction
            cur.execute("""
                INSERT INTO [transaction] 
                (admin_id, account_number, receiver_account, amount, type, status, timestamp)
                VALUES (NULL, ?, NULL, ?, 'Deposit', 'Approved', GETDATE())
            """, (self.selected_account, amount))

            commit_changes(auto_close=True)

            QMessageBox.information(self, "Success", f"Deposited Rs. {amount} successfully!")
            self.amountInput.clear()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
        finally:
            close_connection()

    # ------------------------------------------
    def go_back(self):
        from user_portal import UserPortal
        self.portal = UserPortal(self.user_id)
        self.portal.show()
        self.close()
