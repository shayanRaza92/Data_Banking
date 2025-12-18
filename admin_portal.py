# admin_portal.py
from PyQt6 import QtWidgets, uic
import os
from db_connection import get_cursor, close_connection
from PyQt6.QtWidgets import QMessageBox

class AdminPortal(QtWidgets.QMainWindow):
    def __init__(self, admin_id):
        super(AdminPortal, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "admin_portal.ui"), self)
        
        from ui_styles import apply_style
        apply_style(self)

        self.admin_id = admin_id
        self.admin_role = self.get_admin_role()

        # Show role-based screens
        if self.admin_role == "Manager":
            self.show_manager_options()
        elif self.admin_role == "Accountant":
            self.show_accountant_options()
        else:
            QMessageBox.warning(self, "Error", "Unknown admin role!")

        # Connect Buttons
        self.btnApproveUsers.clicked.connect(self.open_approve_users)
        self.btnViewUsers.clicked.connect(self.open_view_users)
        self.btnDeleteUsers.clicked.connect(self.open_delete_users)
        self.btnApproveLoan.clicked.connect(self.open_approve_loan)
        self.btnViewTransactions.clicked.connect(self.open_view_transactions)

        # NEW BUTTON EVENT
        self.btnApproveTransactions.clicked.connect(self.open_approve_transactions)

        self.btnBack.clicked.connect(self.go_back)

    def get_admin_role(self):
        cur = get_cursor()
        cur.execute("SELECT role FROM admin WHERE admin_id = ?", (self.admin_id,))
        row = cur.fetchone()
        close_connection()
        return row[0] if row else None

    # MANAGER OPTIONS
   
    def show_manager_options(self):
        self.btnApproveUsers.show()
        self.btnViewUsers.show()
        self.btnDeleteUsers.show()
        self.btnApproveLoan.show()

        self.btnViewTransactions.hide()
        self.btnApproveTransactions.hide()

    
    # ACCOUNTANT OPTIONS
    
    def show_accountant_options(self):
        self.btnApproveUsers.hide()
        self.btnViewUsers.hide()
        self.btnDeleteUsers.hide()
        self.btnApproveLoan.hide()

        self.btnViewTransactions.show()
        self.btnApproveTransactions.show()

    
    # Button Handlers
    
    def open_approve_users(self):
        from approve_users import ApproveUsersScreen
        self.x = ApproveUsersScreen(self.admin_id)
        self.x.show()
        self.close()

    def open_view_users(self):
        from view_users import ViewUsersScreen
        self.x = ViewUsersScreen(self.admin_id)
        self.x.show()
        self.close()

    def open_delete_users(self):
        from deactivate_users import DeactivateUsersScreen
        self.x = DeactivateUsersScreen(self.admin_id)
        self.x.show()
        self.close()

    def open_approve_loan(self):
        from approve_loans import ApproveLoanScreen
        self.x = ApproveLoanScreen(self.admin_id)
        self.x.show()
        self.close()

    def open_view_transactions(self):
        from view_transactions import ViewTransactionsScreen
        self.x = ViewTransactionsScreen(self.admin_id)
        self.x.show()
        self.close()

    def open_approve_transactions(self):
        from approve_transactions import ApproveTransactionScreen
        self.x = ApproveTransactionScreen(self.admin_id)
        self.x.show()
        self.close()

    def go_back(self):
        from login import LoginOptions
        self.x = LoginOptions()
        self.x.show()
        self.close()
