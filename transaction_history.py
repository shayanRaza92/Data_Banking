# transaction_history.py
from PyQt6 import QtWidgets, uic
import os
from PyQt6.QtWidgets import QMessageBox
from db_connection import get_cursor, close_connection

class TransactionHistoryScreen(QtWidgets.QMainWindow):
    def __init__(self, user_id):
        super(TransactionHistoryScreen, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "transaction_history.ui"), self)

        from ui_styles import apply_style
        apply_style(self)

        self.user_id = user_id
        self.selected_account = None

        self.btnBack.clicked.connect(self.go_back)
        self.accountCombo.currentIndexChanged.connect(self.update_selected_account)

        # Load user's accounts list
        self.load_accounts()

    # ----------------------------------------------------------
    # LOAD ALL ACCOUNTS OF USER
    # ----------------------------------------------------------
    def load_accounts(self):
        cur = get_cursor()
        try:
            cur.execute("SELECT account_number, type FROM account WHERE user_id = ?", (self.user_id,))
            accounts = cur.fetchall()

            if not accounts:
                QMessageBox.warning(self, "Error", "No accounts found.")
                return

            for acc_num, acc_type in accounts:
                self.accountCombo.addItem(f"{acc_num} – {acc_type}", acc_num)

            # Set selected account and load its transactions
            self.selected_account = self.accountCombo.currentData()
            self.load_transactions()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
        finally:
            close_connection()

    # ----------------------------------------------------------
    # ON ACCOUNT SELECTION CHANGE
    # ----------------------------------------------------------
    def update_selected_account(self):
        self.selected_account = self.accountCombo.currentData()
        self.load_transactions()

    # ----------------------------------------------------------
    # LOAD TRANSACTIONS FOR SELECTED ACCOUNT
    # ----------------------------------------------------------
    def load_transactions(self):
        if self.selected_account is None:
            return

        cur = get_cursor()
        try:
            cur.execute("""
                SELECT 
                    transaction_id,
                    amount,
                    type,
                    status,
                    reason,
                    timestamp
                FROM [transaction]
                WHERE account_number = ?
                ORDER BY timestamp DESC
            """, (self.selected_account,))

            rows = cur.fetchall()

            self.tableTransactions.setRowCount(len(rows))
            self.tableTransactions.setColumnCount(6)

            self.tableTransactions.setHorizontalHeaderLabels([
                "Transaction ID",
                "Amount",
                "Type",
                "Status",
                "Reason",
                "Timestamp"
            ])

            for i, row in enumerate(rows):
                trans_id, amount, t_type, status, reason, time = row

                # Fancy text for pending transfer
                if t_type == "Transfer" and status == 'Pending':
                    t_type = "Transfer (Pending)"
                
                # Show reason only if rejected (or exists)
                reason_text = str(reason) if reason else "-"

                # Insert into table
                self.tableTransactions.setItem(i, 0, QtWidgets.QTableWidgetItem(str(trans_id)))
                self.tableTransactions.setItem(i, 1, QtWidgets.QTableWidgetItem(str(amount)))
                self.tableTransactions.setItem(i, 2, QtWidgets.QTableWidgetItem(t_type))
                self.tableTransactions.setItem(i, 3, QtWidgets.QTableWidgetItem(str(status)))
                self.tableTransactions.setItem(i, 4, QtWidgets.QTableWidgetItem(reason_text))
                self.tableTransactions.setItem(i, 5, QtWidgets.QTableWidgetItem(str(time)))

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
