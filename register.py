from PyQt6 import QtWidgets, uic
import os
from PyQt6.QtWidgets import QMessageBox
import sys, datetime
from db_connection import get_cursor, commit_changes, close_connection

class RegisterScreen(QtWidgets.QMainWindow):
    def __init__(self):
        super(RegisterScreen, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "register.ui"), self)
        
        from ui_styles import apply_style
        apply_style(self)

        # Buttons
        self.btnSubmit.clicked.connect(self.submit_form)
        self.btnBack.clicked.connect(self.go_back)
        self.btnAddPhone.clicked.connect(self.add_phone)

        self.statusLabel.setText("")

    # ---------------------------------------
    # ADD PHONE TO LIST
    # ---------------------------------------
    def add_phone(self):
        phone = self.phoneInput.text().strip()

        if phone == "":
            QMessageBox.warning(self, "Error", "Enter a phone number first.")
            return
            
        if not phone.isdigit():
            QMessageBox.warning(self, "Error", "Phone number must simplify be numeric.")
            return

        # Check existing in LIST
        items = [self.phoneList.item(i).text() for i in range(self.phoneList.count())]
        if phone in items:
            QMessageBox.warning(self, "Error", "Phone number already added to list.")
            return
            
        # Check existing in DATABASE
        try:
             cur = get_cursor()
             cur.execute("SELECT COUNT(*) FROM user_phone WHERE phone = ?", (phone,))
             if cur.fetchone()[0] > 0:
                 QMessageBox.warning(self, "Error", "This phone number is already in use by another user.")
                 close_connection()
                 return
             close_connection()
        except Exception as e:
             QMessageBox.critical(self, "Database Error", str(e))
             close_connection()
             return

        self.phoneList.addItem(phone)
        self.phoneInput.clear()

    # ---------------------------------------
    # SUBMIT FORM
    # ---------------------------------------
    def submit_form(self):
        first = self.firstNameInput.text().strip()
        last = self.lastNameInput.text().strip()
        email = self.emailInput.text().strip()
        password = self.passwordInput.text().strip()
        cnic = self.cnicInput.text().strip()
        street = self.streetInput.text().strip()
        city = self.cityInput.text().strip()

        # VALIDATION
        if not all([first, last, email, password, cnic, street, city]):
            self.statusLabel.setText("All fields are required.")
            return
            
        # Check CNIC numeric
        if not cnic.isdigit():
            QMessageBox.warning(self, "Input Error", "CNIC must be numeric only.")
            return

        if self.phoneList.count() == 0:
            self.statusLabel.setText("Add at least ONE phone number.")
            return

        cur = None
        try:
            cur = get_cursor()

            # CHECK IF EMAIL EXISTS
            cur.execute("SELECT COUNT(*) FROM [user] WHERE email = ?", (email,))
            if cur.fetchone()[0] > 0:
                QMessageBox.warning(
                    self,
                    "Email Exists",
                    f"The email '{email}' is already registered."
                )
                return

            # CHECK IF CNIC EXISTS
            cur.execute("SELECT COUNT(*) FROM [user] WHERE CNIC = ?", (cnic,))
            if cur.fetchone()[0] > 0:
                QMessageBox.warning(
                    self,
                    "CNIC Exists",
                    f"The CNIC '{cnic}' is already registered."
                )
                return

            date_registered = datetime.date.today().strftime("%Y-%m-%d")

            # INSERT USER (NO ACCOUNT TYPE ANYMORE)
            insert_user = """
                INSERT INTO [user]
                (first_name, last_name, email, password, CNIC,
                 Address_Street, Address_City, date_registered, Admin_ID)
                OUTPUT INSERTED.user_id
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL)
            """

            cur.execute(insert_user, (
                first, last, email, password, cnic,
                street, city, date_registered
            ))

            row = cur.fetchone()
            if row is None:
                raise Exception("Failed to retrieve new user ID")

            user_id = row[0]

            # INSERT PHONE NUMBERS
            for i in range(self.phoneList.count()):
                phone = self.phoneList.item(i).text()
                cur.execute(
                    "INSERT INTO user_phone (user_id, phone) VALUES (?, ?)",
                    (user_id, phone)
                )

            commit_changes(auto_close=True)

            QMessageBox.information(
                self,
                "Success",
                "User registered successfully!\nPlease wait for admin approval."
            )

            self.clear_fields()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            if cur:
                try:
                    cur.connection.rollback()
                except:
                    pass
            close_connection()

    # ---------------------------------------
    # CLEAR FIELDS
    # ---------------------------------------
    def clear_fields(self):
        self.firstNameInput.clear()
        self.lastNameInput.clear()
        self.emailInput.clear()
        self.passwordInput.clear()
        self.cnicInput.clear()
        self.streetInput.clear()
        self.cityInput.clear()
        self.phoneList.clear()
        self.phoneInput.clear()
        self.statusLabel.setText("")

    # ---------------------------------------
    # GO BACK
    # ---------------------------------------
    def go_back(self):
        from entry import EntryScreen
        self.entry = EntryScreen()
        self.entry.show()
        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = RegisterScreen()
    window.show()
    app.exec()
