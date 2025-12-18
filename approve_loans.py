# approve_loans.py
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox, QInputDialog, QDateEdit
from db_connection import get_cursor, commit_changes, close_connection
import datetime
import os

class ApproveLoanScreen(QtWidgets.QMainWindow):
    def __init__(self, admin_id):
        super(ApproveLoanScreen, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "approve_loans.ui"), self)

        from ui_styles import apply_style
        apply_style(self)

        self.admin_id = admin_id

        self.btnApprove.clicked.connect(self.approve_loan)
        self.btnReject.clicked.connect(self.reject_loan)
        self.btnBack.clicked.connect(self.go_back)

        self.load_loans()

    # LOAD ALL LOAN REQUESTS WITH admin_id NULL
    
    def load_loans(self):
        cur = get_cursor()
        try:
            cur.execute("""
                SELECT loan_id, account_number, loan_amount, reason, status
                FROM loan
                WHERE admin_id IS NULL AND status = 'Pending'
            """)

            rows = cur.fetchall()

            self.tableLoans.setRowCount(len(rows))
            self.tableLoans.setColumnCount(5)

            self.tableLoans.setHorizontalHeaderLabels([
                "Loan ID",
                "Account Number",
                "Amount",
                "Reason",
                "Status"
            ])

            for r, row in enumerate(rows):
                for c, value in enumerate(row):
                    self.tableLoans.setItem(
                        r, c, QtWidgets.QTableWidgetItem(str(value))
                    )

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))


    
    # APPROVE SELECTED LOAN
    
    def approve_loan(self):
        print("=== approve_loan called ===")
        row = self.tableLoans.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Select a loan request.")
            return

        loan_id = int(self.tableLoans.item(row, 0).text())
        account_number = int(self.tableLoans.item(row, 1).text())
        amount = float(self.tableLoans.item(row, 2).text())
        
        print(f"Loan ID: {loan_id}, Account: {account_number}, Amount: {amount}")

       
        rate, ok = QInputDialog.getDouble(
            self, "Interest Rate", "Enter Interest Rate (%):", decimals=2
        )
        print(f"Interest rate input: {rate}, OK: {ok}")
        if not ok:
            print("User cancelled interest rate input")
            return

        end_date_dialog = QtWidgets.QDialog(self)
        end_date_dialog.setWindowTitle("Select End Date")
        layout = QtWidgets.QVBoxLayout(end_date_dialog)

        date_selector = QDateEdit()
        date_selector.setCalendarPopup(True)
        date_selector.setMinimumDate(datetime.date.today())
        layout.addWidget(date_selector)

        btn_ok = QtWidgets.QPushButton("Approve Loan")
        layout.addWidget(btn_ok)

        btn_ok.clicked.connect(end_date_dialog.accept)

        # Keep a reference so it doesn't get garbage collected
        self._end_date_dialog = end_date_dialog

        result = end_date_dialog.exec()
        print(f"Dialog result: {result}")
        
        if result != 1:  # 1 means accepted, 0 means rejected
            print("User cancelled date selection")
            return

        end_date = date_selector.date().toPyDate()
        start_date = datetime.date.today()
        
        print(f"Start date: {start_date}, End date: {end_date}, Interest rate: {rate}")

        try:
            print("Getting cursor...")
            cur = get_cursor()

            # 1) Update loan entry
            print("Updating loan entry...")
            cur.execute("""
                UPDATE loan
                SET admin_id = ?, interest_rate = ?, start_date = ?, end_date = ?, status = 'Approved'
                WHERE loan_id = ?
            """, (self.admin_id, rate, start_date, end_date, loan_id))
            
            print(f"Rows affected by loan update: {cur.rowcount}")

            # 2) Deposit the loan amount into the account
            print("Updating account balance...")
            cur.execute("""
                UPDATE account
                SET balance = balance + ?
                WHERE account_number = ?
            """, (amount, account_number))
            
            print(f"Rows affected by balance update: {cur.rowcount}")

            print("Committing changes...")
            commit_changes(auto_close=True)
            
            print("Changes committed successfully!")

            QMessageBox.information(self, "Loan Approved",
                                    f"Loan approved!\n{amount} has been deposited.")

            print("Reloading loans table...")
            self.load_loans()
            print("Table reloaded!")

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Database Error", str(e))


    
    # REJECT LOAN REQUEST
    
    def reject_loan(self):
        row = self.tableLoans.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Select a loan to reject.")
            return

        loan_id = int(self.tableLoans.item(row, 0).text())

        confirm = QMessageBox.question(
            self, "Confirm",
            "Reject this loan request?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.No:
            return

        try:
            cur = get_cursor()

            cur.execute("DELETE FROM loan WHERE loan_id = ?", (loan_id,))

            commit_changes(auto_close=True)

            QMessageBox.information(self, "Rejected", "Loan request removed.")
            self.load_loans()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))


    def go_back(self):
        from admin_portal import AdminPortal
        self.portal = AdminPortal(self.admin_id)
        self.portal.show()
        self.close()
