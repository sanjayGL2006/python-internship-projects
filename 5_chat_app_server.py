"""
PROJECT 5: ADVANCED CHAT APPLICATION — SERVER
--------------------------------------------------
Features:
- Socket server supporting multiple clients and multiple chat rooms
- User authentication (simple username/password check against a local file)
- Message history per room (persisted to disk, replayed to new joiners)
- Fernet symmetric encryption for all messages on the wire
- Broadcast notifications when users join/leave

SETUP:
    pip install cryptography

Run this first, then run 5_chat_app_client.py (multiple times for multiple users).
IMPORTANT: server.py and client.py must share the same SECRET_KEY (see key.key file
generated on first run).
"""

import socket
import threading
import json
import os
import datetime
from cryptography.fernet import Fernet

HOST = "0.0.0.0"
PORT = 5050
KEY_FILE = "key.key"
USERS_FILE = "users.json"
HISTORY_DIR = "chat_history"
DEFAULT_ROOMS = ["general", "random", "tech"]


def get_or_create_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    print(f"[SERVER] Generated new encryption key in {KEY_FILE}. Copy this file next to the client script.")
    return key


def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def history_path(room):
    os.makedirs(HISTORY_DIR, exist_ok=True)
    return os.path.join(HISTORY_DIR, f"{room}.log")


def append_history(room, line):
    with open(history_path(room), "a", encoding="utf-8") as f:
        f.write(line + "\n")


def read_history(room, limit=50):
    path = history_path(room)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [l.strip() for l in lines[-limit:]]


class ChatServer:
    def __init__(self):
        self.key = get_or_create_key()
        self.fernet = Fernet(self.key)
        self.users = load_users()
        self.clients = {}  # conn -> {"username": str, "room": str}
        self.lock = threading.Lock()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((HOST, PORT))
        self.sock.listen()
        print(f"[SERVER] Listening on {HOST}:{PORT}")

    def encrypt(self, text):
        return self.fernet.encrypt(text.encode("utf-8"))

    def decrypt(self, token):
        return self.fernet.decrypt(token).decode("utf-8")

    def send_json(self, conn, payload: dict):
        try:
            conn.sendall(self.encrypt(json.dumps(payload)) + b"\n<<END>>\n")
        except Exception:
            pass

    def broadcast(self, room, payload, exclude=None):
        with self.lock:
            for conn, meta in self.clients.items():
                if meta["room"] == room and conn != exclude:
                    self.send_json(conn, payload)

    def recv_json(self, conn, buffer):
        while b"\n<<END>>\n" not in buffer:
            chunk = conn.recv(4096)
            if not chunk:
                return None, buffer
            buffer += chunk
        raw, _, buffer = buffer.partition(b"\n<<END>>\n")
        try:
            return json.loads(self.decrypt(raw)), buffer
        except Exception:
            return None, buffer

    def handle_client(self, conn, addr):
        buffer = b""
        username = None
        try:
            # --- Authentication handshake ---
            msg, buffer = self.recv_json(conn, buffer)
            if msg is None:
                conn.close()
                return
            username = msg.get("username", "").strip()
            password = msg.get("password", "")
            if not username or not password:
                self.send_json(conn, {"type": "auth", "ok": False, "reason": "Missing credentials"})
                conn.close()
                return

            with self.lock:
                if username in self.users:
                    if self.users[username] != password:
                        self.send_json(conn, {"type": "auth", "ok": False, "reason": "Wrong password"})
                        conn.close()
                        return
                else:
                    self.users[username] = password  # simple auto-registration
                    save_users(self.users)

            room = msg.get("room", "general")
            if room not in DEFAULT_ROOMS:
                DEFAULT_ROOMS.append(room)

            with self.lock:
                self.clients[conn] = {"username": username, "room": room}

            self.send_json(conn, {"type": "auth", "ok": True, "rooms": DEFAULT_ROOMS})
            for line in read_history(room):
                self.send_json(conn, {"type": "history", "line": line})

            join_note = f"[{self._now()}] * {username} joined #{room} *"
            append_history(room, join_note)
            self.broadcast(room, {"type": "message", "line": join_note}, exclude=conn)

            # --- Main receive loop ---
            while True:
                msg, buffer = self.recv_json(conn, buffer)
                if msg is None:
                    break

                if msg.get("type") == "switch_room":
                    old_room = self.clients[conn]["room"]
                    new_room = msg["room"]
                    if new_room not in DEFAULT_ROOMS:
                        DEFAULT_ROOMS.append(new_room)
                    with self.lock:
                        self.clients[conn]["room"] = new_room
                    for line in read_history(new_room):
                        self.send_json(conn, {"type": "history", "line": line})
                    note = f"[{self._now()}] * {username} left #{old_room} for #{new_room} *"
                    append_history(old_room, note)
                    self.broadcast(old_room, {"type": "message", "line": note}, exclude=conn)
                    continue

                if msg.get("type") == "message":
                    room = self.clients[conn]["room"]
                    line = f"[{self._now()}] {username}: {msg['text']}"
                    append_history(room, line)
                    self.broadcast(room, {"type": "message", "line": line})

        except (ConnectionResetError, BrokenPipeError):
            pass
        finally:
            with self.lock:
                meta = self.clients.pop(conn, None)
            if meta:
                note = f"[{self._now()}] * {meta['username']} disconnected *"
                append_history(meta["room"], note)
                self.broadcast(meta["room"], {"type": "message", "line": note})
            conn.close()

    @staticmethod
    def _now():
        return datetime.datetime.now().strftime("%H:%M:%S")

    def run(self):
        try:
            while True:
                conn, addr = self.sock.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("\n[SERVER] Shutting down.")
        finally:
            self.sock.close()


if __name__ == "__main__":
    ChatServer().run()
