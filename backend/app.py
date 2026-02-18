from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import requests, json, os, re

from db import get_db_connection

# =================================================
# 🚀 APP INIT
# =================================================
app = Flask(
    __name__,
    static_folder="../frontend/static",
    static_url_path="/static"
)

app.secret_key = "super_secret_key_123"

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

LANGUAGE_MAP = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu"
}

LEVEL_PROMPTS = {
    "basic": "Explain very simply for a school student.",
    "intermediate": "Explain clearly with examples for a college student.",
    "professional": "Explain technically for a science professional."
}

# =================================================
# 🛟 SAFE JSON EXTRACTOR (FIXED)
# =================================================
def safe_json_extract(text):
    if not text:
        raise ValueError("Empty AI response")

    text = text.strip()

    # Extract inside ```json ... ```
    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if fenced:
        text = fenced.group(1).strip()

    # Find first JSON object
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON object found")

    return json.loads(match.group())

# =================================================
# 🤖 AI GENERATION (FULLY FIXED)
# =================================================
def generate_explanation(term, level, language):

    prompt = f"""
Respond ONLY with valid JSON.
No markdown.
No extra text.

Language: {LANGUAGE_MAP.get(language, "English")}
Level: {LEVEL_PROMPTS.get(level)}

JSON FORMAT:
{{
  "definition": "",
  "explanation": [""],
  "advantages": [""],
  "disadvantages": [""],
  "related_terms": [""]
}}

TERM: {term}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 300
                }
            },
            timeout=120  # ⬅ increased timeout
        )

        raw = response.json().get("response", "")
        print("\n🧠 RAW AI OUTPUT:\n", raw)

        parsed = safe_json_extract(raw)

        # Force structure consistency
        def ensure_list(val):
            if isinstance(val, list):
                return val
            if isinstance(val, str):
                return [val]
            return []

        return {
            "definition": parsed.get("definition", ""),
            "explanation": ensure_list(parsed.get("explanation", [])),
            "advantages": ensure_list(parsed.get("advantages", [])),
            "disadvantages": ensure_list(parsed.get("disadvantages", [])),
            "related_terms": ensure_list(parsed.get("related_terms", []))
        }

    except requests.exceptions.Timeout:
        print("❌ AI TIMEOUT ERROR")
        return {
            "definition": f"{term} explanation unavailable.",
            "explanation": ["AI took too long to respond."],
            "advantages": [],
            "disadvantages": [],
            "related_terms": []
        }

    except Exception as e:
        print("❌ AI JSON ERROR:", e)
        return {
            "definition": f"{term} explanation unavailable.",
            "explanation": ["AI response format error."],
            "advantages": [],
            "disadvantages": [],
            "related_terms": []
        }

# =================================================
# 🔹 EXPLAIN API
# =================================================
@app.route("/api/explain", methods=["POST"])
def explain():
    data = request.json or {}
    term = data.get("term", "").strip()
    level = data.get("level", "basic")
    language = data.get("language", "en")

    if not term:
        return jsonify({"error": "Term required"}), 400

    result = generate_explanation(term, level, language)

    # Store prompt in DB
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
# 🔐 AUTH
# =================================================
@app.route("/api/signin", methods=["POST"])
def signin():
    d = request.json
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email=%s", (d["email"],))
    user = cur.fetchone()

    if not user or not check_password_hash(user["password"], d["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    session.clear()
    session.update({
        "user_id": user["id"],
        "username": user["username"],
        "role": user["role"]
    })

    return jsonify({"success": True})

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})

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
# 🚀 RUN
# =================================================
if __name__ == "__main__":
    app.run(debug=True)
