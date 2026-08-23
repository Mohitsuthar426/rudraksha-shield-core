import sqlite3
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DB_NAME = "rudraksha_enterprise.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        plan TEXT DEFAULT 'STARTER_TIER',
        license_key TEXT,
        valid_until TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

def hash_pw(pw):
    return hashlib.sha256(f"rudra_salt_{pw}".encode()).hexdigest()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    pw = data.get("password", "").strip()

    if not name or not email or not pw:
        return jsonify({"status": "ERROR", "message": "Badha fields required chhe!"}), 400

    lic_key = f"RUDRA-START-{secrets.token_hex(4).upper()}"
    expiry = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO users (name, email, password_hash, plan, license_key, valid_until) VALUES (?, ?, ?, ?, ?, ?)",
                  (name, email, hash_pw(pw), "STARTER_TIER", lic_key, expiry))
        conn.commit()
        conn.close()
        return jsonify({"status": "SUCCESS", "message": "Account register thai gayu! Have Login karo."})
    except sqlite3.IntegrityError:
        return jsonify({"status": "ERROR", "message": "Aa Email pehla thi registered chhe!"}), 409

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    pw = data.get("password", "").strip()

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, email, plan, license_key, valid_until FROM users WHERE email=? AND password_hash=?", (email, hash_pw(pw)))
    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({
            "status": "SUCCESS",
            "user": {
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "plan": user[3],
                "license_key": user[4],
                "valid_until": user[5]
            }
        })
    return jsonify({"status": "ERROR", "message": "Email athva Password khoto chhe!"}), 401

@app.route('/api/payment/upgrade', methods=['POST'])
def upgrade_plan():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()

    new_lic = f"RUDRA-ENT-{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}"
    new_expiry = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET plan='ENTERPRISE_UNLIMITED', license_key=?, valid_until=? WHERE email=?", (new_lic, new_expiry, email))
    conn.commit()
    conn.close()

    return jsonify({
        "status": "SUCCESS",
        "message": "Payment Verified! Enterprise License Activated.",
        "plan": "ENTERPRISE_UNLIMITED",
        "license_key": new_lic,
        "valid_until": new_expiry
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
