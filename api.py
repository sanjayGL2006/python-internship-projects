"""
Custom API key system (Flask + SQLite).

Run:
    pip install flask
    export ADMIN_TOKEN="pick-a-long-random-string"     # Windows: set ADMIN_TOKEN=...
    python app.py

Create a key (admin only):
    curl -X POST http://127.0.0.1:5000/admin/keys \
         -H "X-Admin-Token: $ADMIN_TOKEN" -H "Content-Type: application/json" \
         -d '{"name": "client-app-1"}'

Use the key:
    curl -X POST http://127.0.0.1:5000/v1/generate \
         -H "X-API-Key: spvm_..." -H "Content-Type: application/json" \
         -d '{"prompt": "Hello"}'
"""
import hashlib
import hmac
import os
import secrets
import sqlite3
from functools import wraps

from flask import Flask, g, jsonify, request, render_template

app = Flask(__name__)
DB_FILE = "api_keys.db"
KEY_PREFIX = "spvm_"
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")

if not ADMIN_TOKEN:
    raise SystemExit("Set the ADMIN_TOKEN environment variable before starting.")


# ---------- Database ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_FILE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                key_prefix TEXT NOT NULL,          -- first chars, safe to display
                key_hash TEXT UNIQUE NOT NULL,     -- SHA-256 of the full key
                revoked INTEGER NOT NULL DEFAULT 0,
                request_count INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used_at TIMESTAMP
            )
            """
        )


def hash_key(key: str) -> str:
    # Keys are long and random, so a fast hash is fine (no salt/slow hash needed).
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


# ---------- Auth decorators ----------
def require_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        supplied = request.headers.get("X-Admin-Token", "")
        if not hmac.compare_digest(supplied, ADMIN_TOKEN):
            return jsonify(error="Admin authorization required."), 401
        return fn(*args, **kwargs)
    return wrapper


def require_api_key(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        key = request.headers.get("X-API-Key")
        if not key:
            return jsonify(error="Missing X-API-Key header."), 401

        db = get_db()
        row = db.execute(
            "SELECT id, name, revoked FROM api_keys WHERE key_hash = ?",
            (hash_key(key),),
        ).fetchone()

        if row is None or row["revoked"]:
            return jsonify(error="Invalid or revoked API key."), 403

        db.execute(
            "UPDATE api_keys SET request_count = request_count + 1, "
            "last_used_at = CURRENT_TIMESTAMP WHERE id = ?",
            (row["id"],),
        )
        db.commit()
        g.client_name = row["name"]
        return fn(*args, **kwargs)
    return wrapper


# ---------- Admin: manage keys ----------
@app.post("/admin/keys")
@require_admin
def create_key():
    name = (request.get_json(silent=True) or {}).get("name", "").strip()
    if not name:
        return jsonify(error="'name' is required."), 400

    raw_key = KEY_PREFIX + secrets.token_urlsafe(32)
    db = get_db()
    db.execute(
        "INSERT INTO api_keys (name, key_prefix, key_hash) VALUES (?, ?, ?)",
        (name, raw_key[:10], hash_key(raw_key)),
    )
    db.commit()
    return jsonify(
        message="Save this key now. It cannot be shown again.",
        name=name,
        api_key=raw_key,
    ), 201


@app.get("/admin/keys")
@require_admin
def list_keys():
    rows = get_db().execute(
        "SELECT id, name, key_prefix, revoked, request_count, created_at, last_used_at "
        "FROM api_keys ORDER BY id"
    ).fetchall()
    return jsonify(keys=[dict(r) for r in rows])


@app.delete("/admin/keys/<int:key_id>")
@require_admin
def revoke_key(key_id):
    db = get_db()
    cur = db.execute("UPDATE api_keys SET revoked = 1 WHERE id = ?", (key_id,))
    db.commit()
    if cur.rowcount == 0:
        return jsonify(error="Key not found."), 404
    return jsonify(message="Key revoked.")


# ---------- Your protected model endpoint ----------
def run_model(prompt: str) -> str:
    """Replace this with your real model call (local LLM, scikit-learn model, etc.)."""
    return f"(model output for: {prompt})"


@app.post("/v1/generate")
@require_api_key
def generate():
    prompt = (request.get_json(silent=True) or {}).get("prompt", "").strip()
    if not prompt:
        return jsonify(error="'prompt' is required."), 400
    return jsonify(client=g.client_name, response=run_model(prompt))


@app.get("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)