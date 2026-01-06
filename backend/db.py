import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin@123",        # 👉 MySQL password
        database="lexicon_ai"
    )
