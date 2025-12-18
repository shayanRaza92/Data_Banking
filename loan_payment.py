from PyQt6 import QtWidgets, uic
import os
import sys

class LoanPaymentScreen(QtWidgets.QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "loan_payment.ui"), self)

        from ui_styles import apply_style
        apply_style(self)

        self.user_id = user_id

        self.btnPay.clicked.connect(self.payment)
        self.btnBack.clicked.connect(self.go_back)
        
        # Load Data
        self.load_source_accounts()
        self.load_loan_accounts()

    def load_source_accounts(self):
        """Loads user's active accounts into sourceAccountCombo."""
        try:
            from db_connection import get_cursor, close_connection
            cursor = get_cursor()
            # User requested to pay from Loan accounts as well, so we remove the filter
            query = "SELECT account_number, type, balance FROM account WHERE user_id = ?"
            cursor.execute(query, (self.user_id,))
            rows = cursor.fetchall()
            
            self.sourceAccountCombo.clear()
            self.sourceAccountCombo.addItem("Select Source Account")
            
            for row in rows:
                # Format: "Savings - 10001 (Bal: 5000)"
                display_text = f"{row.type} - {row.account_number} (Bal: {row.balance})"
                self.sourceAccountCombo.addItem(display_text, userData=row.account_number)

            close_connection()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load accounts: {str(e)}")

    def load_loan_accounts(self):
        """Loads user's APPROVED loans into loanAccountCombo."""
        try:
            from db_connection import get_cursor, close_connection
            
            cursor = get_cursor()
            
            # Join Loan and Account to get loan details
            # We want loans that are 'Approved'
            query = """
                SELECT L.loan_id, L.account_number, L.loan_amount, L.status
                FROM loan L
                JOIN account A ON L.account_number = A.account_number
                WHERE A.user_id = ? AND L.status = 'Approved'
            """
            cursor.execute(query, (self.user_id,))
            rows = cursor.fetchall()
            
            self.loanAccountCombo.clear()
            self.loanAccountCombo.addItem("Select Loan Account")
            
            for row in rows:
                # Format: "Loan #5 - Acc: 10005 (Amount: 50000)"
                display_text = f"Loan #{row.loan_id} - Acc: {row.account_number} (Amt: {row.loan_amount})"
                # Store tuple (loan_id, account_number) or just loan_id
                self.loanAccountCombo.addItem(display_text, userData={'loan_id': row.loan_id, 'acc_num': row.account_number, 'amount': row.loan_amount})

            close_connection()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load loans: {str(e)}")

    def payment(self):
        amount_text = self.amountInput.text()
        
        # 1. Validation
        if not amount_text.isdigit():
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please enter a valid numeric amount.")
            return
            
        amount = float(amount_text)
        if amount <= 0:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Amount must be greater than 0.")
            return

        # 2. Get Selected Accounts
        source_idx = self.sourceAccountCombo.currentIndex()
        loan_idx = self.loanAccountCombo.currentIndex()
        
        if source_idx <= 0 or loan_idx <= 0:
            QtWidgets.QMessageBox.warning(self, "Selection Error", "Please select both a source account and a loan account.")
            return
            
        source_acc_num = self.sourceAccountCombo.currentData()
        loan_data = self.loanAccountCombo.currentData()
        loan_id = loan_data['loan_id']
        loan_acc_num = loan_data['acc_num']
        
        # 3. Process Payment
        try:
            import datetime
            from db_connection import get_cursor, commit_changes, close_connection
            
            cursor = get_cursor()
            
            # Check Balance of Source
            cursor.execute("SELECT balance FROM account WHERE account_number = ?", (source_acc_num,))
            current_balance = cursor.fetchval()
            
            if current_balance < amount:
                QtWidgets.QMessageBox.warning(self, "Insufficient Funds", f"Source account balance ({current_balance}) is too low.")
                close_connection()
                return

            # Execute Transaction
            # 1. Deduct from Source
            cursor.execute("UPDATE account SET balance = balance - ? WHERE account_number = ?", (amount, source_acc_num))
            
            # 2. Insert into Loan Payment
            cursor.execute("""
                INSERT INTO loan_payment (loan_id, payment_date, amount_paid)
                VALUES (?, ?, ?)
            """, (loan_id, datetime.datetime.now(), amount))
            
            # 3. Update Loan Amount (Reduce Debt)
            cursor.execute("UPDATE loan SET loan_amount = loan_amount - ? WHERE loan_id = ?", (amount, loan_id))
            
            # 4. Update Status to 'Paid' if amount is 0 or less
            cursor.execute("UPDATE loan SET status = 'Paid' WHERE loan_id = ? AND loan_amount <= 0", (loan_id,))

            # 5. Record Transaction (Source -> Bank/Loan)
            # Receiver account is NULL (Bank internal)
            cursor.execute("""
                INSERT INTO [transaction] (account_number, amount, type, status, timestamp, receiver_account)
                VALUES (?, ?, 'Loan Payment', 'Approved', ?, NULL)
            """, (source_acc_num, amount, datetime.datetime.now()))
            
            commit_changes()
            
            QtWidgets.QMessageBox.information(self, "Success", f"Payment of {amount} processed successfully.")
            
            # Refresh UI
            self.load_source_accounts()
            # Reload loans too, in case one just got paid off and should disappear (assuming load_loan_accounts filters by Approved)
            self.load_loan_accounts() 
            self.amountInput.clear()
            
            close_connection()
            
        except Exception as e:
            # db_connection doesn't expose rollback directly on cursor, but typically unexpected errors might need manual handling or rely on transaction behaviour.
            # However, our shared module connects/commits. 
            print(f"Transaction Failed: {e}")
            QtWidgets.QMessageBox.critical(self, "Transaction Failed", f"Error processing payment: {str(e)}")


    def go_back(self):
        from user_portal import UserPortal
        self.portal = UserPortal(self.user_id)
        self.portal.show()
        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = LoanPaymentScreen(1)
    win.show()
    app.exec()
