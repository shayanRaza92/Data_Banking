# 🏦 Data Banking System

Welcome to the **Data Banking System**! 👋

This is a comprehensive desktop banking application built with **Python (PyQt6)** and **SQL Server**. It provides a secure and user-friendly platform for managing bank accounts, transactions, and loans.

## 🌟 Features

*   **User Portal**: View balance, transfer funds, pay loans, and view transaction history.
*   **Admin Portal**: Approve permissions, manage loans, and oversee system activity.
*   **Secure Auth**: Role-based login and registration system.
*   **Interactive UI**: Modern and clean interface designed with PyQt6.

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:
*   Python 3.8+
*   SQL Server (with ODBC Driver 17)
*   Git

## 🚀 Getting Started

Follow these steps to get the project up and running on your local machine.

### 1. Clone the Repository
```bash
git clone https://github.com/shayanRaza92/Data_Banking.git
cd Data_Banking
```

### 2. Install Dependencies
Install the required Python packages:
```bash
pip install PyQt6 pyodbc
```

### 3. 🗄️ Database Setup (Crucial Step!)
**You must set up the database before running the application.**

1.  Open **SQL Server Management Studio (SSMS)**.
2.  Open the file `project_ddl.sql` from this repository.
3.  Execute the script. This will create the `BankingDB` database and all necessary tables.

### 4. Configure Connection
Open `db_connection.py` and ensure the connection string matches your local SQL Server instance:
```python
# Example in db_connection.py
conn_str = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=YOUR_SERVER_NAME;"  # <--- Update this if needed
    r"DATABASE=BankingDB;"
    r"Trusted_Connection=yes;"
)
```

## ▶️ How to Run

Once the database is ready, you can launch the application:

```bash
python entry.py
```

## 🤝 Contributing
Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

---
*Built with ❤️ by Shayan Raza*
