from PyQt6 import QtWidgets, uic
import os
from db_connection import get_cursor, close_connection

class ViewBalanceScreen(QtWidgets.QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "view_balance.ui"), self)

        from ui_styles import apply_style
        apply_style(self)

        self.user_id = user_id

        self.btnCheck.clicked.connect(self.check_balance)
        self.btnBack.clicked.connect(self.go_back)

        self.load_accounts()

    # ----------------------------
    # Load user's accounts
    # ----------------------------
    def load_accounts(self):
        cur = get_cursor()
        cur.execute("SELECT account_number, type FROM account WHERE user_id = ?", (self.user_id,))
        accounts = cur.fetchall()
        close_connection()

        for acc_no, acc_type in accounts:
            self.accountCombo.addItem(f"{acc_no} ({acc_type})", acc_no)

    # ----------------------------
    # Check balance
    # ----------------------------
    def check_balance(self):
        selected_acc = self.accountCombo.currentData()

        cur = get_cursor()
        cur.execute("SELECT balance FROM account WHERE account_number = ?", (selected_acc,))
        bal = cur.fetchone()
        close_connection()

        if bal:
            self.labelBalance.setText(f"Balance: Rs. {bal[0]}")
        else:
            self.labelBalance.setText("Balance not found.")

    # ----------------------------
    # Go back to User Portal
    # ----------------------------
    def go_back(self):
        import user_portal
        self.portal = user_portal.UserPortal(self.user_id)
        self.portal.show()
        self.hide()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    win = ViewBalanceScreen(1)
    win.show()
    app.exec()