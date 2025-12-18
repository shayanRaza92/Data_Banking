# create_account.py
from PyQt6 import QtWidgets, uic
import os
from PyQt6.QtWidgets import QMessageBox
from db_connection import get_cursor, commit_changes, close_connection

class CreateAccountScreen(QtWidgets.QMainWindow):
    def __init__(self, user_id):
        super(CreateAccountScreen, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "create_account.ui"), self)

        from ui_styles import apply_style
        apply_style(self)

        self.user_id = user_id

        self.btnNormal.clicked.connect(lambda: self.create_account("Normal"))
        self.btnLoan.clicked.connect(lambda: self.create_account("Loan"))
        self.btnBack.clicked.connect(self.go_back)

    # -------------------------------------------------------
    # CREATE ACCOUNT FUNCTION
    # -------------------------------------------------------
    def create_account(self, acc_type):
        try:
            cur = get_cursor()

            # Insert a new account with zero balance
            cur.execute("""
                INSERT INTO account (user_id, type, balance, date_created, status)
                VALUES (?, ?, 0, GETDATE(), 'Active')
            """, (self.user_id, acc_type))

            commit_changes(auto_close=True)

            QMessageBox.information(
                self,
                "Success",
                f"{acc_type} account created successfully!"
            )

            self.go_back()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            close_connection()

    # -------------------------------------------------------
    # GO BACK TO USER PORTAL
    # -------------------------------------------------------
    def go_back(self):
        from user_portal import UserPortal
        self.portal = UserPortal(self.user_id)
        self.portal.show()
        self.close()
