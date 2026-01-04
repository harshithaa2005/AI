from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from db import get_db_connection

app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)

@app.route('/')
def home():
    return send_file('../frontend/home.html')

# ---------------- SIGN UP ----------------
@app.route("/signup", methods=["POST"], endpoint="signup_post")
def signup():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        conn.close()
        return jsonify({"message": "User already exists"}), 400

    # Insert new user
    cursor.execute(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        (username, email, password)
    )
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Signup successful"}), 201


# ---------------- SIGN IN ----------------
@app.route("/signin", methods=["POST"])
def signin():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password)
    )
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"]
            }
        }), 200
    else:
        return jsonify({"message": "Invalid email or password"}), 401


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(debug=True)
