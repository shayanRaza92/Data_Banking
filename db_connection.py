import pyodbc
import datetime


#  DATABASE CONNECTION CONFIGURATION

server = r'VICTUS\SQLSERVER'
database = 'Data_Banking1'
use_windows_authentication = True
username = ''
password = ''

#  CONNECTION STRING SETUP

if use_windows_authentication:
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};DATABASE={database};Trusted_Connection=yes;"
    )
else:
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )

connection = None
cursor = None

#  DATABASE CONNECTION 

def connect():
    """Establish a new connection to SQL Server."""
    global connection, cursor
    try:
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        print(f" Connected to {database} at {server} ({datetime.datetime.now().strftime('%H:%M:%S')})")
    except pyodbc.Error as e:
        print(" Database connection error:", e)
        connection, cursor = None, None
def get_cursor():
    """Returns a live database cursor; reconnects if needed."""
    global connection, cursor
    if connection is None or cursor is None:
        connect()
    return cursor


def commit_changes(auto_close=False):
    """Commit changes to the database."""
    global connection
    if connection:
        connection.commit()

    if auto_close:
        close_connection()


def execute_query(query, params=None, fetch=False):
    """
    Executes a query safely.
    fetch = True ONLY for SELECT queries.
    INSERT/UPDATE/DELETE must use fetch=False
    """
    cur = get_cursor()
    try:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)

        if fetch:
            return cur.fetchall()

        return None

    except Exception as e:
        print(" Query Error:", e)
        raise


def close_connection():
    """Close database connection and cursor."""
    global cursor, connection
    if cursor:
        try:
            cursor.close()
        except:
            pass
        cursor = None
    if connection:
        try:
            connection.close()
        except:
            pass
        connection = None