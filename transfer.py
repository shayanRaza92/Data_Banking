# transfer.py
from PyQt6 import QtWidgets, uic
import os
from PyQt6.QtWidgets import QMessageBox
from db_connection import get_cursor, commit_changes, close_connection

class TransferScreen(QtWidgets.QMainWindow):
    def __init__(self, user_id):
        super(TransferScreen, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "transfer.ui"), self)

        from ui_styles import apply_style
        apply_style(self)

        self.user_id = user_id
        self.sender_account = None

        self.btnTransfer.clicked.connect(self.request_transfer)
        self.btnBack.clicked.connect(self.go_back)

        self.load_accounts()

        # update when user selects different account
        self.accountCombo.currentIndexChanged.connect(self.update_selected_account)

    # ----------------------------------------------------------
    def load_accounts(self):
        """Load all accounts belonging to this user."""
        cur = get_cursor()
        try:
            cur.execute("SELECT account_number, type, balance FROM account WHERE user_id = ?", (self.user_id,))
            accounts = cur.fetchall()

            if not accounts:
                QMessageBox.critical(self, "Error", "No accounts found for this user.")
                return

            self.accountCombo.clear()
            for acc_num, acc_type, balance in accounts:
                # Show: 1001 – Normal (Bal: 500.0)
                self.accountCombo.addItem(f"{acc_num} – {acc_type} (Bal: {balance})", acc_num)

            # Set initial selected account
            self.sender_account = self.accountCombo.currentData()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

        finally:
            close_connection()

    # ----------------------------------------------------------
    def update_selected_account(self):
        self.sender_account = self.accountCombo.currentData()

    # ----------------------------------------------------------
    def request_transfer(self):
        if self.sender_account is None:
            QMessageBox.warning(self, "Error", "Please select an account first.")
            return

        receiver = self.receiverInput.text().strip()
        amount_text = self.amountInput.text().strip()

        # Validate receiver
        if not receiver.isdigit():
            QMessageBox.warning(self, "Invalid Input", "Receiver account number must be numeric.")
            return

        receiver = int(receiver)

        if receiver == self.sender_account:
            QMessageBox.warning(self, "Error", "You cannot transfer to your own account.")
            return

        # Validate amount
        if not amount_text.isdigit():
            QMessageBox.warning(self, "Invalid Amount", "Amount must be numeric.")
            return

        amount = float(amount_text)

        if amount <= 0:
            QMessageBox.warning(self, "Invalid Amount", "Amount must be greater than zero.")
            return

        try:
            cur = get_cursor()

            # Check receiver exists
            cur.execute("SELECT COUNT(*) FROM account WHERE account_number = ?", (receiver,))
            if cur.fetchone()[0] == 0:
                QMessageBox.warning(self, "Error", "Receiver account does not exist.")
                return

            # Check Sender Balance
            cur.execute("SELECT balance FROM account WHERE account_number = ?", (self.sender_account,))
            balance = cur.fetchval()
            
            if balance is None:
                 # Should not happen if foreign key is correct, but safe to check
                 QMessageBox.critical(self, "Error", "Account not found.")
                 return

            if balance < amount:
                QMessageBox.warning(self, "Insufficient Funds", f"Your balance is only {balance}. Cannot transfer {amount}.")
                return

            # Create pending transfer
            cur.execute("""
                INSERT INTO [transaction]
                (admin_id, account_number, receiver_account, amount, type, status, timestamp)
                VALUES (NULL, ?, ?, ?, 'Transfer', 'Pending', GETDATE())
            """, (self.sender_account, receiver, amount))

            commit_changes(auto_close=True)

            QMessageBox.information(
                self,
                "Transfer Requested",
                "Your transfer request has been submitted.\nIt will be approved by an accountant."
            )

            self.receiverInput.clear()
            self.amountInput.clear()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

        finally:
            close_connection()

    # ----------------------------------------------------------
    def go_back(self):
        from user_portal import UserPortal
        self.portal = UserPortal(self.user_id)
        self.portal.show()
        self.close()
