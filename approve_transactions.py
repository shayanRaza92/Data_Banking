# approve_transactions.py
from PyQt6 import QtWidgets, uic
import os
from PyQt6.QtWidgets import QMessageBox
from db_connection import get_cursor, commit_changes, close_connection

class ApproveTransactionScreen(QtWidgets.QMainWindow):
    def __init__(self, admin_id):
        super(ApproveTransactionScreen, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "approve_transactions.ui"), self)

        from ui_styles import apply_style
        apply_style(self)

        self.admin_id = admin_id

        self.btnApprove.clicked.connect(self.approve_transaction)
        self.btnReject.clicked.connect(self.reject_transaction)
        self.btnBack.clicked.connect(self.go_back)

        self.load_transfers()

    # ---------------------------------------------------------
    # LOAD ALL PENDING TRANSFERS (WHERE admin_id IS NULL)
    # ---------------------------------------------------------
    def load_transfers(self):
        cur = get_cursor()
        try:
            cur.execute("""
                SELECT transaction_id, 
                       account_number AS sender_account,
                       receiver_account,
                       amount,
                       timestamp
                FROM [transaction]
                WHERE type = 'Transfer' AND status = 'Pending'
            """)

            rows = cur.fetchall()

            self.tableTransfers.setRowCount(len(rows))
            self.tableTransfers.setColumnCount(5)

            self.tableTransfers.setHorizontalHeaderLabels([
                "Transaction ID",
                "Sender Account",
                "Receiver Account",
                "Amount",
                "Timestamp"
            ])

            for r, row in enumerate(rows):
                for c, value in enumerate(row):
                    self.tableTransfers.setItem(
                        r, c, QtWidgets.QTableWidgetItem(str(value))
                    )

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
        finally:
            close_connection()

    # ---------------------------------------------------------
    # APPROVE TRANSFER REQUEST
    # ---------------------------------------------------------
    def approve_transaction(self):
        row = self.tableTransfers.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Select a transfer to approve.")
            return

        transaction_id = int(self.tableTransfers.item(row, 0).text())
        sender_account = int(self.tableTransfers.item(row, 1).text())
        receiver_account = int(self.tableTransfers.item(row, 2).text())
        amount = float(self.tableTransfers.item(row, 3).text())

        try:
            cur = get_cursor()

            # Validate receiver exists
            cur.execute("SELECT COUNT(*) FROM account WHERE account_number = ?", (receiver_account,))
            if cur.fetchone()[0] == 0:
                QMessageBox.warning(self, "Error", "Receiver account does not exist.")
                return

            # Check sender balance
            cur.execute("SELECT balance FROM account WHERE account_number = ?", (sender_account,))
            sender_balance = float(cur.fetchone()[0])

            if sender_balance < amount:
                QMessageBox.warning(self, "Error", "Sender does not have enough balance.")
                return

            # Deduct from sender
            cur.execute("""
                UPDATE account
                SET balance = balance - ?
                WHERE account_number = ?
            """, (amount, sender_account))

            # Add to receiver
            cur.execute("""
                UPDATE account
                SET balance = balance + ?
                WHERE account_number = ?
            """, (amount, receiver_account))

            # Mark pending transfer as approved
            cur.execute("""
                UPDATE [transaction]
                SET admin_id = ?, status = 'Approved'
                WHERE transaction_id = ?
            """, (self.admin_id, transaction_id))

            # Add receiver "Transfer Received" entry
            # IMPORTANT: receiver_account MUST BE NULL
            cur.execute("""
                INSERT INTO [transaction] 
                (admin_id, account_number, receiver_account, amount, type, status, timestamp)
                VALUES (?, ?, NULL, ?, 'Transfer Received', 'Approved', GETDATE())
            """, (self.admin_id, receiver_account, amount))

            commit_changes(auto_close=True)

            QMessageBox.information(self, "Success", "Transfer approved successfully.")
            self.load_transfers()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            close_connection()

    # ---------------------------------------------------------
    # REJECT TRANSFER REQUEST
    # ---------------------------------------------------------
    def reject_transaction(self):
        row = self.tableTransfers.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Select a transfer to reject.")
            return

        transaction_id = int(self.tableTransfers.item(row, 0).text())

        # PROMPT FOR REASON
        reason, ok = QtWidgets.QInputDialog.getText(self, "Reject Transaction", "Reason for rejection:")
        
        if not ok or not reason.strip():
            QMessageBox.warning(self, "Cancelled", "Rejection cancelled. Reason is required.")
            return

        try:
            cur = get_cursor()

            # MARK AS REJECTED with REASON
            cur.execute("""
                UPDATE [transaction]
                SET status = 'Rejected', admin_id = ?, reason = ?
                WHERE transaction_id = ?
            """, (self.admin_id, reason, transaction_id))

            commit_changes(auto_close=True)

            QMessageBox.information(self, "Rejected", "Transfer request rejected.")
            self.load_transfers()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            close_connection()

    # ---------------------------------------------------------
    # GO BACK TO ADMIN PORTAL
    # ---------------------------------------------------------
    def go_back(self):
        from admin_portal import AdminPortal
        self.x = AdminPortal(self.admin_id)
        self.x.show()
        self.close()
