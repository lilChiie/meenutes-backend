import urllib.parse

DB_HOST = "LAPTOP-L8OG95QS"
DB_NAME = "meeting_management_db"

params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={DB_HOST};"
    f"DATABASE={DB_NAME};"
    f"Trusted_Connection=yes;"
)

SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={params}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
