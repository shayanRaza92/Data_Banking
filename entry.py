# entry.py
from PyQt6 import QtWidgets, uic
import sys
import os
from login import LoginOptions

class EntryScreen(QtWidgets.QMainWindow):
    def __init__(self):
        super(EntryScreen, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "entry.ui"), self)

        from ui_styles import apply_style
        apply_style(self)

        self.btnLogin.clicked.connect(self.open_login)
        self.btnRegister.clicked.connect(self.open_register)

    def open_login(self):
        self.login_window = LoginOptions()
        self.login_window.show()
        self.close()

    def open_register(self):
        from register import RegisterScreen
        self.register_window = RegisterScreen()
        self.register_window.show()
        self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = EntryScreen()
    window.show()
    app.exec()
