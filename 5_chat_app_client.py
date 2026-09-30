"""
PROJECT 5: ADVANCED CHAT APPLICATION — CLIENT
--------------------------------------------------
Features:
- Tkinter GUI chat window
- Login screen (username/password — auto-registers new users on the server)
- Multi-room support with a dropdown to switch rooms
- Displays message history on join/room switch
- Fernet-encrypted communication (matching key.key from the server)
- Emoji support: type standard emoji directly (Tkinter/Tk renders unicode emoji)

SETUP:
    pip install cryptography

IMPORTANT: copy the server's generated `key.key` file into the same folder as
this client script before connecting.
"""

import socket
import threading
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from cryptography.fernet import Fernet

HOST = "127.0.0.1"   # change to the server's IP if connecting remotely
PORT = 5050
KEY_FILE = "key.key"


class ChatClient:
    def __init__(self, root):
        self.root = root
        root.title("Chat Application")
        root.geometry("520x600")

        if not os.path.exists(KEY_FILE):
            messagebox.showerror(
                "Missing key",
                f"'{KEY_FILE}' not found. Copy it from the server folder into this client's folder.",
            )
            root.destroy()
            return

        with open(KEY_FILE, "rb") as f:
            self.fernet = Fernet(f.read())

        self.sock = None
        self.buffer = b""
        self.current_room = "general"
        self.rooms = ["general"]

        self._build_login_screen()

    # ---------------- Login ----------------
    def _build_login_screen(self):
        self.login_frame = ttk.Frame(self.root, padding=30)
        self.login_frame.pack(fill="both", expand=True)

        ttk.Label(self.login_frame, text="Chat Login", font=("Segoe UI", 16, "bold")).pack(pady=10)

        ttk.Label(self.login_frame, text="Username:").pack(anchor="w")
        self.username_var = tk.StringVar()
        ttk.Entry(self.login_frame, textvariable=self.username_var).pack(fill="x", pady=4)

        ttk.Label(self.login_frame, text="Password:").pack(anchor="w")
        self.password_var = tk.StringVar()
        ttk.Entry(self.login_frame, textvariable=self.password_var, show="*").pack(fill="x", pady=4)

        ttk.Label(self.login_frame, text="Room:").pack(anchor="w")
        self.room_var = tk.StringVar(value="general")
        ttk.Entry(self.login_frame, textvariable=self.room_var).pack(fill="x", pady=4)

        ttk.Button(self.login_frame, text="Connect", command=self.connect).pack(pady=14)

    def connect(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()
        room = self.room_var.get().strip() or "general"
        if not username or not password:
            messagebox.showerror("Missing info", "Enter a username and password.")
            return

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))
        except Exception as e:
            messagebox.showerror("Connection failed", str(e))
            return

        self.username = username
        self._send_json({"username": username, "password": password, "room": room})
        response, self.buffer = self._recv_json()

        if not response or not response.get("ok"):
            reason = response.get("reason") if response else "No response from server"
            messagebox.showerror("Login failed", reason)
            self.sock.close()
            return

        self.rooms = response.get("rooms", ["general"])
        self.current_room = room
        self.login_frame.destroy()
        self._build_chat_screen()
        threading.Thread(target=self._listen_loop, daemon=True).start()

    # ---------------- Chat UI ----------------
    def _build_chat_screen(self):
        top = ttk.Frame(self.root, padding=8)
        top.pack(fill="x")
        ttk.Label(top, text=f"Logged in as {self.username}").pack(side="left")

        ttk.Label(top, text="  Room:").pack(side="left")
        self.room_combo = ttk.Combobox(top, values=self.rooms, width=15)
        self.room_combo.set(self.current_room)
        self.room_combo.pack(side="left", padx=4)
        ttk.Button(top, text="Switch", command=self.switch_room).pack(side="left", padx=2)
        ttk.Button(top, text="New Room", command=self.new_room).pack(side="left", padx=2)

        self.chat_box = tk.Text(self.root, state="disabled", wrap="word")
        self.chat_box.pack(fill="both", expand=True, padx=8, pady=6)

        bottom = ttk.Frame(self.root, padding=8)
        bottom.pack(fill="x")
        self.message_var = tk.StringVar()
        entry = ttk.Entry(bottom, textvariable=self.message_var)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        entry.bind("<Return>", lambda e: self.send_message())
        ttk.Button(bottom, text="Send 😀", command=self.send_message).pack(side="left")

    def switch_room(self):
        new_room = self.room_combo.get().strip()
        if not new_room or new_room == self.current_room:
            return
        self._append(f"--- switching to #{new_room} ---")
        self._send_json({"type": "switch_room", "room": new_room})
        self.current_room = new_room

    def new_room(self):
        name = simpledialog.askstring("New Room", "Room name:")
        if name:
            self.rooms.append(name)
            self.room_combo["values"] = self.rooms
            self.room_combo.set(name)
            self.switch_room()

    def send_message(self):
        text = self.message_var.get().strip()
        if not text or not self.sock:
            return
        self._send_json({"type": "message", "text": text})
        self.message_var.set("")

    # ---------------- Networking ----------------
    def _send_json(self, payload: dict):
        try:
            token = self.fernet.encrypt(json.dumps(payload).encode("utf-8"))
            self.sock.sendall(token + b"\n<<END>>\n")
        except Exception as e:
            self._append(f"[error sending message: {e}]")

    def _recv_json(self):
        buffer = self.buffer
        while b"\n<<END>>\n" not in buffer:
            chunk = self.sock.recv(4096)
            if not chunk:
                return None, buffer
            buffer += chunk
        raw, _, buffer = buffer.partition(b"\n<<END>>\n")
        try:
            data = json.loads(self.fernet.decrypt(raw).decode("utf-8"))
        except Exception:
            data = None
        return data, buffer

    def _listen_loop(self):
        while True:
            try:
                msg, self.buffer = self._recv_json()
            except Exception:
                break
            if msg is None:
                self._append("[disconnected from server]")
                break
            if msg.get("type") in ("message", "history"):
                self._append(msg["line"])

    def _append(self, text):
        def do_append():
            self.chat_box.configure(state="normal")
            self.chat_box.insert(tk.END, text + "\n")
            self.chat_box.configure(state="disabled")
            self.chat_box.see(tk.END)
        self.root.after(0, do_append)


if __name__ == "__main__":
    root = tk.Tk()
    ChatClient(root)
    root.mainloop()
