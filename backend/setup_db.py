import mysql.connector

# Connect to MySQL server
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin@123"   # 👉 put your MySQL password
)

cursor = conn.cursor()

# Create database
cursor.execute("CREATE DATABASE IF NOT EXISTS lexicon_ai")
cursor.execute("USE lexicon_ai")

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
)
""")

# Create prompts table for storing user prompts and AI responses
cursor.execute("""
CREATE TABLE IF NOT EXISTS prompts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    user_prompt TEXT NOT NULL,
    ai_response LONGTEXT NOT NULL,
    level VARCHAR(50),
    language VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Create reviews table for storing user reviews
cursor.execute("""
CREATE TABLE IF NOT EXISTS ai_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    term VARCHAR(255),
    language VARCHAR(50),
    stars INT,
    review TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
cursor.close()
conn.close()

print("✅ Database and users table created successfully")
