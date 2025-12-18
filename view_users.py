from PyQt6 import QtWidgets, uic
import os
from PyQt6.QtWidgets import QMessageBox
from db_connection import get_cursor, close_connection

class ViewUsersScreen(QtWidgets.QMainWindow):
    def __init__(self, admin_id):
        super(ViewUsersScreen, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "view_users.ui"), self)

        from ui_styles import apply_style
        apply_style(self)

        self.admin_id = admin_id

        self.btnBack.clicked.connect(self.go_back)

        self.load_users()

    # ---------------------------------------------------------
    # LOAD USERS APPROVED BY THIS ADMIN (Consolidating accounts)
    # ---------------------------------------------------------
    def load_users(self):
        cur = get_cursor()
        try:
            # Fetch all user and account data, sorted by user_id
            cur.execute("""
                SELECT 
                    u.user_id,
                    u.first_name,
                    u.last_name,
                    u.email,
                    u.CNIC,
                    u.Address_Street,
                    u.Address_City,
                    u.date_registered,
                    a.account_number,
                    a.type
                FROM [user] u
                LEFT JOIN account a ON u.user_id = a.user_id
                WHERE u.Admin_ID = ?
                ORDER BY u.user_id
            """, (self.admin_id,))

            rows = cur.fetchall()

            # Dictionary to consolidate data: Key is user_id
            consolidated_users = {}

            # --- Data Consolidation ---
            for row in rows:
                user_id = row[0]
                
                # Base user data (Columns 0-7)
                user_details = list(row[:8]) 
                
                # Account data (Columns 8, 9)
                account_number = row[8]
                account_type = row[9]

                if user_id not in consolidated_users:
                    # Initialize the user's entry
                    consolidated_users[user_id] = {
                        'details': user_details,
                        'accounts': [],
                        'types': []
                    }
                
                # Append account info if it exists (non-None, handles users with no accounts)
                if account_number is not None:
                    consolidated_users[user_id]['accounts'].append(str(account_number))
                    consolidated_users[user_id]['types'].append(str(account_type))
                
            # Prepare the final table data
            final_table_data = []
            for user_id, data in consolidated_users.items():
                
                # 1. Start with the 8 user detail columns (0-7)
                final_row = data['details'] 
                
                # 2. Join all accounts into one string (Column 8)
                # If there are no accounts, show 'N/A'
                account_numbers_str = '\n'.join(data['accounts']) if data['accounts'] else 'N/A'
                final_row.append(account_numbers_str)
                
                # 3. Join all types into one string (Column 9)
                account_types_str = '\n'.join(data['types']) if data['types'] else 'N/A'
                final_row.append(account_types_str)
                
                final_table_data.append(final_row)


            # --- Display Data in Table ---
            
            # Number of unique users determines the rows
            self.tableUsers.setRowCount(len(final_table_data)) 
            # Still 10 columns (8 user details + 1 consolidated account number + 1 consolidated account type)
            self.tableUsers.setColumnCount(10) 

            self.tableUsers.setHorizontalHeaderLabels([
                "User ID",
                "First Name",
                "Last Name",
                "Email",
                "CNIC",
                "Street",
                "City",
                "Registered On",
                "Account Numbers",  # Consolidated column
                "Account Types"     # Consolidated column
            ])

            for row_index, row_data in enumerate(final_table_data):
                for col_index, value in enumerate(row_data):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    self.tableUsers.setItem(row_index, col_index, item)
            
            # Ensure the table can show multi-line content (optional but recommended for multi-account display)
            self.tableUsers.resizeRowsToContents() 

            # hide user_id visually but keep in backend
            self.tableUsers.setColumnHidden(0, True)

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