# view_transactions.py
from PyQt6 import QtWidgets, uic
import os
from PyQt6.QtWidgets import QMessageBox
from db_connection import get_cursor, close_connection

class ViewTransactionsScreen(QtWidgets.QMainWindow):
    def __init__(self, admin_id):     
        super(ViewTransactionsScreen, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "view_transactions.ui"), self)
        
        from ui_styles import apply_style
        apply_style(self)

        self.admin_id = admin_id

        self.btnBack.clicked.connect(self.go_back)

        self.load_transactions()

    
    def load_transactions(self):
        cur = get_cursor()
        try:
            cur.execute("""
                SELECT transaction_id, account_number, amount, type, status, reason, timestamp
                FROM [transaction]
                WHERE 
                    type IN ('Deposit', 'Withdraw', 'Loan Payment')
                    OR type = 'Transfer'
                ORDER BY timestamp DESC
            """)

            rows = cur.fetchall()

            self.tableTrans.setRowCount(len(rows))
            self.tableTrans.setColumnCount(7)

            self.tableTrans.setHorizontalHeaderLabels([
                "Transaction ID",
                "Account Number",
                "Amount",
                "Type",
                "Status",
                "Reason",
                "Timestamp"
            ])

            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    self.tableTrans.setItem(i, j, QtWidgets.QTableWidgetItem(str(value) if value is not None else ""))

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

        finally:
            close_connection()

    
    def go_back(self):
        from admin_portal import AdminPortal
        self.portal = AdminPortal(self.admin_id)
        self.portal.show()
        self.close()
