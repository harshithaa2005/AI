import sqlite3
import os

def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'lexicon_ai.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # To access columns by name
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    
    return conn
