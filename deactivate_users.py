from PyQt6 import QtWidgets, uic
import os
from PyQt6.QtWidgets import QMessageBox
from db_connection import get_cursor, commit_changes, close_connection

class DeactivateUsersScreen(QtWidgets.QMainWindow):
    def __init__(self, admin_id):
        super(DeactivateUsersScreen, self).__init__()
        # Ensure your 'deactivate_users.ui' has 7 visible columns plus 1 hidden column (user_id)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "deactivate_users.ui"), self) 
        
        from ui_styles import apply_style
        apply_style(self)

        self.admin_id = admin_id

        self.btnDeactivate.clicked.connect(self.deactivate_user)
        self.btnBack.clicked.connect(self.go_back)

        self.load_users()

    # ---------------------------------------------------------
    # LOAD users (ONLY ONE ROW PER USER)
    # ---------------------------------------------------------
    def load_users(self):
        cur = get_cursor()
        try:
            # Note: We remove the LEFT JOIN to 'account' and 'account_number' from the SELECT list.
            # We now only query the user details, grouped by user_id to ensure unique rows.
            cur.execute("""
                SELECT 
                    u.user_id,
                    u.first_name,
                    u.last_name,
                    u.email,
                    u.CNIC,
                    u.Address_Street,
                    u.Address_City
                FROM [user] u
                WHERE u.Admin_ID = ?
                GROUP BY 
                    u.user_id, u.first_name, u.last_name, u.email, 
                    u.CNIC, u.Address_Street, u.Address_City
            """, (self.admin_id,))

            rows = cur.fetchall()

            # The table now has 7 columns visible (plus the hidden user_id)
            self.tableUsers.setRowCount(len(rows))
            self.tableUsers.setColumnCount(7) 

            self.tableUsers.setHorizontalHeaderLabels([
                "User ID (Hidden)", # Column 0
                "First Name",       # Column 1
                "Last Name",        # Column 2
                "Email",            # Column 3
                "CNIC",             # Column 4
                "Street",           # Column 5
                "City"              # Column 6
            ])

            for i, row in enumerate(rows):
                for j in range(7):
                    self.tableUsers.setItem(i, j, QtWidgets.QTableWidgetItem(str(row[j])))

            # hide user_id
            self.tableUsers.setColumnHidden(0, True)

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
        finally:
            close_connection()

    # ---------------------------------------------------------
    # NEW: CHECK ALL ACCOUNTS OF A USER FOR PENDING LOANS
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # NEW: CHECK ALL ACCOUNTS OF A USER FOR ACTIVE/PENDING LOANS
    # ---------------------------------------------------------
    def user_has_active_or_pending_loan(self, user_id):
        cur = get_cursor()
        try:
            cur.execute("""
                SELECT COUNT(*)
                FROM loan l
                INNER JOIN account a ON l.account_number = a.account_number
                WHERE a.user_id = ? AND l.status IN ('Pending', 'Approved')
            """, (user_id,))
            
            count = cur.fetchone()[0]
            return count > 0
        except Exception as e:
            QMessageBox.critical(self, "Loan Check Error", f"Failed to check loans: {str(e)}")
            return True
        finally:
            close_connection()

    # ---------------------------------------------------------
    # DEACTIVATE USER
    # ---------------------------------------------------------
    def deactivate_user(self):
        row = self.tableUsers.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Select a user first.")
            return

        user_id = int(self.tableUsers.item(row, 0).text())
        
        # 1. CHECK LOANS (Pending OR Approved)
        if self.user_has_active_or_pending_loan(user_id):
            QMessageBox.warning(
                self,
                "Cannot Deactivate",
                "User has pending or approved (unpaid) loans. Clear loans first."
            )
            return

        # Check for non-zero balance
        try:
            cur = get_cursor()
            cur.execute("SELECT SUM(balance) FROM account WHERE user_id = ?", (user_id,))
            total_balance = cur.fetchone()[0]
            if total_balance and total_balance > 0:
                 QMessageBox.warning(
                    self,
                    "Cannot Deactivate",
                    f"User still has a total balance of {total_balance}. Accounts must be empty."
                )
                 close_connection()
                 return
            close_connection()
        except Exception as e:
             QMessageBox.critical(self, "Error", str(e))
             close_connection()
             return

        # Prompt for deactivation reason
        reason, ok = QtWidgets.QInputDialog.getText(self, "Deactivation Reason", "Reason for deactivation:")
        if not ok or not reason.strip():
            QMessageBox.warning(self, "Cancelled", "Deactivation cancelled. Reason is required.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm",
            "This will archive and delete all user accounts/transactions. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.No:
            return

        try:
            cur = get_cursor()

            # Get user accounts
            cur.execute("SELECT account_number FROM account WHERE user_id = ?", (user_id,))
            account_numbers = [row[0] for row in cur.fetchall()]

            # Archive User
            cur.execute("""
                INSERT INTO archived_user (original_user_id, first_name, last_name, email, password, CNIC, Address_Street, Address_City, date_registered, deactivated_by_admin_id, deactivation_reason)
                SELECT user_id, first_name, last_name, email, password, CNIC, Address_Street, Address_City, date_registered, ?, ?
                FROM [user]
                WHERE user_id = ?
            """, (self.admin_id, reason, user_id))

            if account_numbers:
                placeholders = ','.join(['?'] * len(account_numbers))
                
                # Archive Transactions
                cur.execute(f"""
                    INSERT INTO archived_transaction (original_trans_id, account_number, receiver_account, amount, type, timestamp, admin_id, status, reason)
                    SELECT transaction_id, account_number, receiver_account, amount, type, timestamp, admin_id, status, reason
                    FROM [transaction]
                    WHERE account_number IN ({placeholders}) OR receiver_account IN ({placeholders})
                """, account_numbers + account_numbers)

                # Archive Accounts
                cur.execute("""
                    INSERT INTO archived_account (original_account_number, user_id, type, balance, date_created)
                    SELECT account_number, user_id, type, balance, date_created
                    FROM account
                    WHERE user_id = ?
                """, (user_id,))

                # Delete Transactions
                cur.execute(f"DELETE FROM [transaction] WHERE account_number IN ({placeholders})", account_numbers)
            
                # Delete Loans
                cur.execute(f"DELETE FROM loan_payment WHERE loan_id IN (SELECT loan_id FROM loan WHERE account_number IN ({placeholders}))", account_numbers)
                cur.execute(f"DELETE FROM loan WHERE account_number IN ({placeholders})", account_numbers)
                
                # Delete Accounts
                cur.execute("DELETE FROM account WHERE user_id = ?", (user_id,))
            
            # Delete Phone
            cur.execute("DELETE FROM user_phone WHERE user_id = ?", (user_id,))

            # Delete User
            cur.execute("DELETE FROM [user] WHERE user_id = ?", (user_id,))

            commit_changes(auto_close=True)

            QMessageBox.information(self, "Success", "User deactivated and data archived.")
            self.load_users()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
        finally:
            close_connection()

    # ---------------------------------------------------------
    # BACK BUTTON
    # ---------------------------------------------------------
    def go_back(self):
        from admin_portal import AdminPortal
        self.portal = AdminPortal(self.admin_id)
        self.portal.show()
        self.close()