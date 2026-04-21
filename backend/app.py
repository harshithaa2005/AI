from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import requests, json, os, re, secrets

from db import get_db_connection

# =================================================
# 🚀 APP INIT
# =================================================
app = Flask(
    __name__,
    static_folder="../frontend/static",
    static_url_path="/static"
)

app.secret_key = secrets.token_hex(16)

app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    PERMANENT_SESSION_LIFETIME=timedelta(days=1)
)

CORS(app, supports_credentials=True)

BASE_DIR = os.path.dirname(__file__)
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
UI_LANG_DIR = os.path.join(BASE_DIR, "ui_languages")

# =================================================
# 🌍 FRONTEND ROUTES
# =================================================
@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "homepage.html")

@app.route("/signin")
def signin_page():
    return send_from_directory(FRONTEND_DIR, "signin.html")

@app.route("/signup")
def signup_page():
    return send_from_directory(FRONTEND_DIR, "signup.html")

@app.route("/admin")
def admin_page():
    return send_from_directory(FRONTEND_DIR, "admin.html")

@app.route("/history")
def history_page():
    return send_from_directory(FRONTEND_DIR, "history.html")

# =================================================
# 🌐 UI LANGUAGE API
# =================================================
@app.route("/api/ui-language/<lang>")
def ui_language(lang):
    path = os.path.join(UI_LANG_DIR, f"{lang}.json")
    if not os.path.exists(path):
        path = os.path.join(UI_LANG_DIR, "en.json")
    with open(path, "r", encoding="utf-8") as f:
        return jsonify(json.load(f))

# =================================================
# 🤖 OLLAMA CONFIG
# =================================================
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "phi3:mini"

# =================================================
# 🛟 SAFE JSON
# =================================================
def safe_json_extract(text):
    text = text.strip()
    match = re.search(r"\{[\s\S]*\}", text)
    return json.loads(match.group()) if match else {}

# =================================================
# 🤖 AI FUNCTION
# =================================================
def generate_explanation(term):
    return {
        "definition": f"{term} definition",
        "explanation": ["Sample explanation"],
        "advantages": [],
        "disadvantages": [],
        "related_terms": []
    }

# =================================================
# 🔹 EXPLAIN API (SAVES HISTORY)
# =================================================
@app.route("/api/explain", methods=["POST"])
def explain():
    data = request.json or {}
    term = data.get("term", "").strip()
    level = data.get("level", "basic")
    language = data.get("language", "en")

    if not term:
        return jsonify({"error": "Term required"}), 400

    result = generate_explanation(term)

    # SAVE HISTORY
    if "user_id" in session:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO prompts (user_id, term, level, language) VALUES (%s,%s,%s,%s)",
            (session["user_id"], term, level, language)
        )
        conn.commit()
        cur.close()
        conn.close()

    return jsonify(result)

# =================================================
# 📜 HISTORY API
# =================================================
@app.route("/api/history")
def get_history():

    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT term, level, language, created_at
        FROM prompts
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (session["user_id"],))

    history = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(history)

# =================================================
# 🔐 SIGNUP (FIXED)
# =================================================
@app.route("/api/signup", methods=["POST"])
def signup():
    d = request.json

    username = d.get("username")
    email = d.get("email")
    password = d.get("password")

    if not username or not email or not password:
        return jsonify({"error": "All fields required"}), 400

    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users (username, email, password, role) VALUES (%s,%s,%s,%s)",
            (username, email, hashed_password, "user")
        )
        conn.commit()
    except Exception:
        return jsonify({"error": "User already exists"}), 400
    finally:
        cur.close()
        conn.close()

    return jsonify({"success": True})

# =================================================
# 🔐 SIGNIN (FIXED)
# =================================================
@app.route("/api/signin", methods=["POST"])
def signin():
    d = request.json

    email = d.get("email")
    password = d.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    cur.close()
    conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid password"}), 401

    session.clear()
    session.update({
        "user_id": user["id"],
        "username": user["username"],
        "role": user["role"]
    })

    return jsonify({
        "success": True,
        "role": user["role"]
    })

# =================================================
# 🔐 LOGOUT
# =================================================
@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})

# =================================================
# 🔐 CHECK LOGIN
# =================================================
@app.route("/api/check-login")
def check_login():
    if "user_id" in session:
        return jsonify({
            "logged_in": True,
            "username": session["username"],
            "role": session["role"]
        })
    return jsonify({"logged_in": False})

# =================================================
# 👑 ADMIN STATS
# =================================================
@app.route("/api/admin/stats")
def admin_stats():

    if "user_id" not in session or session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT COUNT(*) AS total_users FROM users")
    total_users = cur.fetchone()["total_users"]

    cur.execute("SELECT COUNT(*) AS total_prompts FROM prompts")
    total_prompts = cur.fetchone()["total_prompts"]

    cur.execute("""
        SELECT term, COUNT(*) AS count
        FROM prompts
        GROUP BY term
        ORDER BY count DESC
        LIMIT 5
    """)
    top_terms = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({
        "total_users": total_users,
        "total_prompts": total_prompts,
        "top_terms": top_terms
    })

# =================================================
# 🚀 RUN
# =================================================
if __name__ == "__main__":
    app.run(debug=True)