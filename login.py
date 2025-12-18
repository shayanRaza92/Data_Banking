# login.py
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox
import sys
import os
from db_connection import get_cursor, close_connection
class LoginOptions(QtWidgets.QMainWindow):
    def __init__(self):
        super(LoginOptions, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "login.ui"), self)
        
        from ui_styles import apply_style
        apply_style(self)

        self.btnUserLogin.clicked.connect(self.open_user_login)
        self.btnAdminLogin.clicked.connect(self.open_admin_login)
        self.btnBack.clicked.connect(self.go_back)

    def open_user_login(self):
        self.user_login = UserLoginScreen()
        self.user_login.show()
        self.close()

    def open_admin_login(self):
        self.admin_login = AdminLoginScreen()
        self.admin_login.show()
        self.close()

    def go_back(self):
        from entry import EntryScreen
        self.entry = EntryScreen()
        self.entry.show()
        self.close()

# USER LOGIN SCREEN
class UserLoginScreen(QtWidgets.QMainWindow):
    def __init__(self):
        super(UserLoginScreen, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "user_login.ui"), self)
        
        from ui_styles import apply_style
        apply_style(self)

        self.btnLogin.clicked.connect(self.user_login)
        self.btnBack.clicked.connect(self.go_back)

    def user_login(self):
        email = self.emailInput.text().strip()
        password = self.passwordInput.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Error", "Please enter both email and password.")
            return

        cur = get_cursor()
        if not cur:
            QMessageBox.critical(self, "Error", "Failed to connect to database.")
            return

        try:
            cur.execute("""
                SELECT user_id, first_name, Admin_ID
                FROM [user]
                WHERE email = ? AND password = ?
            """, (email, password))

            row = cur.fetchone()

            if not row:
                QMessageBox.warning(self, "Login Failed", "Invalid user credentials.")
                return

            user_id, first_name, admin_id = row
            if admin_id is None:
                QMessageBox.warning(
                    self,
                    "Approval Pending",
                    "Your account approval is pending.\nPlease wait for admin approval."
                )
                return
            QMessageBox.information(self, "Login Successful", f"Welcome, {first_name}!")
            from user_portal import UserPortal
            self.portal = UserPortal(user_id)
            self.portal.show()
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

        finally:
            close_connection()

    def go_back(self):
        from login import LoginOptions
        self.options = LoginOptions()
        self.options.show()
        self.close()

# ADMIN LOGIN SCREEN
class AdminLoginScreen(QtWidgets.QMainWindow):
    def __init__(self):
        super(AdminLoginScreen, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "admin_login.ui"), self)

        from ui_styles import apply_style
        apply_style(self)

        self.btnLogin.clicked.connect(self.admin_login)
        self.btnBack.clicked.connect(self.go_back)

    def admin_login(self):
        email = self.emailInput.text().strip()
        password = self.passwordInput.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Error", "Please enter both email and password.")
            return

        cur = get_cursor()
        if not cur:
            QMessageBox.critical(self, "Error", "Failed to connect to database.")
            return

        try:
            cur.execute("""
                SELECT admin_id, first_name, role
                FROM admin
                WHERE email = ? AND password = ?
            """, (email, password))

            admin = cur.fetchone()

            if not admin:
                QMessageBox.warning(self, "Login Failed", "Invalid admin credentials.")
                return

            admin_id, admin_name, admin_role = admin

            QMessageBox.information(
                self,
                "Login Successful",
                f"Welcome, {admin_name}!"
            )

            from admin_portal import AdminPortal
            self.portal = AdminPortal(admin_id)
            self.portal.show()
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

        finally:
            close_connection()

    def go_back(self):
        self.options = LoginOptions()
        self.options.show()
        self.close()

# MAIN
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LoginOptions()
    window.show()
    app.exec()
