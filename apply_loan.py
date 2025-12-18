# apply_loan.py
from PyQt6 import QtWidgets, uic
import os
from PyQt6.QtWidgets import QMessageBox
from db_connection import get_cursor, commit_changes, close_connection

class ApplyLoanScreen(QtWidgets.QMainWindow):
    def __init__(self, user_id):
        super(ApplyLoanScreen, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "apply_loan.ui"), self)

        from ui_styles import apply_style
        apply_style(self)

        self.user_id = user_id

        self.btnApply.clicked.connect(self.submit_loan_request)
        self.btnBack.clicked.connect(self.go_back)

        self.load_loan_accounts()

    
    # LOAD ONLY LOAN ACCOUNTS
    
    def load_loan_accounts(self):
        cur = get_cursor()
        try:
            cur.execute("""
                SELECT account_number 
                FROM account
                WHERE user_id = ? AND type = 'Loan'
            """, (self.user_id,))

            accounts = cur.fetchall()

            if not accounts:
                QMessageBox.warning(self, "No Loan Accounts",
                                    "You do not have any loan accounts to request a loan.")
                return

            for acc in accounts:
                acc_num = acc[0]
                self.loanAccountCombo.addItem(f"{acc_num}", acc_num)

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

        finally:
            close_connection()

    
    # APPLY FOR LOAN
    
    def submit_loan_request(self):
        selected_account = self.loanAccountCombo.currentData()
        amount_text = self.amountInput.text().strip()
        reason = self.reasonInput.toPlainText().strip()

        # Validate selections
        if selected_account is None:
            QMessageBox.warning(self, "Error", "Select a loan account first.")
            return

        # Validate amount
        if not amount_text.isdigit():
            QMessageBox.warning(self, "Invalid Amount", "Loan amount must be numeric.")
            return

        amount = float(amount_text)
        if amount <= 0:
            QMessageBox.warning(self, "Invalid Amount", "Amount must be greater than zero.")
            return

        if reason == "":
            QMessageBox.warning(self, "Invalid Reason", "Please enter a reason for the loan.")
            return

        try:
            cur = get_cursor()

            # Check existing loan status
            cur.execute("""
                SELECT status 
                FROM loan 
                WHERE account_number = ?
            """, (selected_account,))

            row = cur.fetchone()

            if row:
                status = row[0]

                if status == "Pending":
                    QMessageBox.warning(self, "Loan Already Pending",
                                        "You already have a pending loan request for this account.")
                    return

                if status == "Approved":
                    QMessageBox.warning(self, "Loan Already Approved",
                                        "You already have an approved loan for this account.")
                    return

            # Insert new loan request
            cur.execute("""
                INSERT INTO loan 
                (account_number, admin_id, loan_amount, interest_rate, start_date, end_date, status, reason)
                VALUES (?, NULL, ?, NULL, NULL, NULL, 'Pending', ?)
            """, (selected_account, amount, reason))

            commit_changes(auto_close=True)

            QMessageBox.information(self, "Success",
                                    "Loan request submitted successfully.\n"
                                    "Please wait for manager approval.")

            self.amountInput.clear()
            self.reasonInput.clear()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

        finally:
            close_connection()

    def go_back(self):
        from user_portal import UserPortal
        self.portal = UserPortal(self.user_id)
        self.portal.show()
        self.close()
