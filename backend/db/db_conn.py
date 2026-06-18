import mysql.connector
import os
DB_HOST = os.environ.get("DB_HOST", "db")
DB_PORT = os.environ.get("DB_PORT", 3306)
DB_USER = os.environ.get("DB_USER", "cafeteria_user")
DB_PASS = os.environ.get("DB_PASS", "cafeteria_pass")
DB_NAME = os.environ.get("DB_NAME", "cafeteria")
def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )