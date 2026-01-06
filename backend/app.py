from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from db import get_db_connection

app = Flask(__name__)

# 🔐 Required for sessions
app.secret_key = "super_secret_key_123"

# Enable CORS with session support
CORS(app, supports_credentials=True)

# ---------------- SIGNUP ----------------
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"message": "User already exists"}), 400

    # Insert new user
    cursor.execute(
        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
        (username, email, password)
    )
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Signup successful"}), 201


# ---------------- SIGNIN ----------------
@app.route("/api/signin", methods=["POST"])
def signin():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE email=%s AND password=%s",
        (email, password)
    )
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        # Store user info in session
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["email"] = user["email"]

        return jsonify({
            "message": "Login successful",
            "username": user["username"]
        }), 200

    return jsonify({"message": "Invalid email or password"}), 401


# ---------------- CHECK LOGIN ----------------
@app.route("/api/check-login", methods=["GET"])
def check_login():
    if "user_id" in session:
        return jsonify({
            "logged_in": True,
            "username": session["username"]
        })
    return jsonify({"logged_in": False})


# ---------------- LOGOUT ----------------
@app.route("/api/logout", methods=["GET"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})


# ---------------- SERVE FRONTEND ----------------
@app.route("/")
def home():
    return send_from_directory("../frontend", "homepage.html")

@app.route("/signin")
def signin_page():
    return send_from_directory("../frontend", "signin.html")

@app.route("/signup")
def signup_page():
    return send_from_directory("../frontend", "signup.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory("../frontend", filename)


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
