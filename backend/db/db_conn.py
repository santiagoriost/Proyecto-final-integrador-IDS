import mysql.connector
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="rios",
        password="santilol",
        database="cafeteria"
    )