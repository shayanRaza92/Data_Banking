# approve_users.py
from PyQt6 import QtWidgets, uic
import os
from PyQt6.QtWidgets import QMessageBox
from db_connection import get_cursor, commit_changes, close_connection

class ApproveUsersScreen(QtWidgets.QMainWindow):
    def __init__(self, admin_id):
        super(ApproveUsersScreen, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "approve_users.ui"), self)

        from ui_styles import apply_style
        apply_style(self)

        self.admin_id = admin_id

        self.btnApprove.clicked.connect(self.approve_user)
        self.btnDisapprove.clicked.connect(self.disapprove_user)
        self.btnBack.clicked.connect(self.go_back)

        self.load_pending_users()

    # ---------------------------------------------------------
    # LOAD users whose Admin_ID IS NULL
    # ---------------------------------------------------------
    def load_pending_users(self):
        cur = get_cursor()
        try:
            cur.execute("""
                SELECT 
                    user_id,
                    first_name,
                    last_name,
                    email,
                    CNIC,
                    Address_Street,
                    Address_City,
                    date_registered
                FROM [user]
                WHERE Admin_ID IS NULL
            """)

            rows = cur.fetchall()

            self.tableUsers.setRowCount(len(rows))
            self.tableUsers.setColumnCount(8)

            self.tableUsers.setHorizontalHeaderLabels([
                "User ID",
                "First Name",
                "Last Name",
                "Email",
                "CNIC",
                "Street",
                "City",
                "Registered On"
            ])

            for i, row in enumerate(rows):
                for j in range(8):
                    self.tableUsers.setItem(i, j, QtWidgets.QTableWidgetItem(str(row[j])))

            # hide user_id from display but keep for logic
            self.tableUsers.setColumnHidden(0, True)

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
        finally:
            close_connection()

    # ---------------------------------------------------------
    # APPROVE USER (ONLY set Admin_ID)
    # ---------------------------------------------------------
    def approve_user(self):
        row = self.tableUsers.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Select a user first.")
            return

        user_id = int(self.tableUsers.item(row, 0).text())

        try:
            cur = get_cursor()

            # Approve user by assigning admin_id
            cur.execute("""
                UPDATE [user]
                SET Admin_ID = ?
                WHERE user_id = ?
            """, (self.admin_id, user_id))

            commit_changes(auto_close=True)

            QMessageBox.information(self, "Approved", "User approved successfully.")
            self.load_pending_users()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            close_connection()

    # ---------------------------------------------------------
    # DISAPPROVE USER (DELETE)
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # DISAPPROVE USER (REJECT & ARCHIVE)
    # ---------------------------------------------------------
    def disapprove_user(self):
        row = self.tableUsers.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Select a user first.")
            return

        user_id = int(self.tableUsers.item(row, 0).text())

        # PROMPT FOR REASON
        reason, ok = QtWidgets.QInputDialog.getText(self, "Reject User", "Reason for rejection:")
        
        if not ok or not reason.strip():
            QMessageBox.warning(self, "Cancelled", "Rejection cancelled. Reason is required.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm",
            "This will move the user to the Rejected Users list and delete the registration request. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.No:
            return

        try:
            cur = get_cursor()

            # Archive to rejected_user
            cur.execute("""
                INSERT INTO rejected_user 
                (original_user_id, first_name, last_name, email, password, CNIC, Address_Street, Address_City, date_registered, rejected_by_admin_id, rejection_reason, rejection_date)
                SELECT 
                    user_id, first_name, last_name, email, password, CNIC, Address_Street, Address_City, date_registered, ?, ?, GETDATE()
                FROM [user]
                WHERE user_id = ?
            """, (self.admin_id, reason, user_id))

            # Delete Phone and User
            cur.execute("DELETE FROM user_phone WHERE user_id = ?", (user_id,))
            cur.execute("DELETE FROM [user] WHERE user_id = ?", (user_id,))

            commit_changes(auto_close=True)

            QMessageBox.information(self, "Rejected", "User registration rejected and archived.")
            self.load_pending_users()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            close_connection()

    # ---------------------------------------------------------
    # GO BACK
    # ---------------------------------------------------------
    def go_back(self):
        from admin_portal import AdminPortal
        self.portal = AdminPortal(self.admin_id)
        self.portal.show()
        self.close()
