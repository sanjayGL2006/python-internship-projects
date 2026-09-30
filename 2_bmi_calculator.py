"""
PROJECT 2: ADVANCED BMI CALCULATOR
------------------------------------
Features:
- Tkinter GUI: input weight (kg) & height (m), pick/create a user profile
- BMI calculation + category classification
- SQLite storage of every entry per user (historical data)
- Trend chart of BMI over time using matplotlib embedded in Tkinter
- Input validation with friendly error messages

SETUP:
    pip install matplotlib
RUN :
     uv run python 2_bmi_calculator.py    
"""

import sqlite3
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib # pyright: ignore[reportMissingModuleSource]
matplotlib.use("TkAgg")
from matplotlib.figure import Figure # type: ignore
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # type: ignore

DB_FILE = "bmi_data.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            weight_kg REAL NOT NULL,
            height_m REAL NOT NULL,
            bmi REAL NOT NULL,
            category TEXT NOT NULL,
            recorded_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def classify_bmi(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def save_record(username, weight, height, bmi, category):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO records (username, weight_kg, height_m, bmi, category, recorded_at) VALUES (?, ?, ?, ?, ?, ?)",
        (username, weight, height, bmi, category, datetime.datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()


def get_history(username):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "SELECT bmi, recorded_at FROM records WHERE username = ? ORDER BY recorded_at ASC",
        (username,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_all_usernames():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT username FROM records")
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows


class BMIApp:
    def __init__(self, root):
        self.root = root
        root.title("Advanced BMI Calculator")
        root.geometry("560x600")

        # --- User selection ---
        frame_user = ttk.LabelFrame(root, text="User Profile")
        frame_user.pack(fill="x", padx=10, pady=8)

        self.username_var = tk.StringVar()
        self.user_combo = ttk.Combobox(frame_user, textvariable=self.username_var, values=get_all_usernames())
        self.user_combo.pack(side="left", padx=8, pady=8, fill="x", expand=True)
        ttk.Button(frame_user, text="Refresh", command=self.refresh_users).pack(side="left", padx=4)

        # --- Inputs ---
        frame_input = ttk.LabelFrame(root, text="Measurements")
        frame_input.pack(fill="x", padx=10, pady=8)

        ttk.Label(frame_input, text="Weight (kg):").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.weight_var = tk.StringVar()
        ttk.Entry(frame_input, textvariable=self.weight_var).grid(row=0, column=1, padx=8, pady=6)

        ttk.Label(frame_input, text="Height (m):").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.height_var = tk.StringVar()
        ttk.Entry(frame_input, textvariable=self.height_var).grid(row=1, column=1, padx=8, pady=6)

        ttk.Button(frame_input, text="Calculate & Save", command=self.calculate).grid(
            row=2, column=0, columnspan=2, pady=10
        )

        # --- Result ---
        self.result_var = tk.StringVar(value="Enter your details above.")
        ttk.Label(root, textvariable=self.result_var, font=("Segoe UI", 13, "bold")).pack(pady=6)

        # --- Chart ---
        frame_chart = ttk.LabelFrame(root, text="BMI Trend")
        frame_chart.pack(fill="both", expand=True, padx=10, pady=8)

        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=frame_chart)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        ttk.Button(root, text="Show Trend for Selected User", command=self.plot_trend).pack(pady=6)

    def refresh_users(self):
        self.user_combo["values"] = get_all_usernames()

    def calculate(self):
        username = self.username_var.get().strip()
        if not username:
            messagebox.showerror("Missing user", "Please enter or select a username.")
            return
        try:
            weight = float(self.weight_var.get())
            height = float(self.height_var.get())
            if weight <= 0 or height <= 0:
                raise ValueError
            if height > 3:  # sanity check: probably entered cm
                raise ValueError("Height should be in meters, e.g. 1.75")
        except ValueError:
            messagebox.showerror("Invalid input", "Enter valid positive numbers (height in meters).")
            return

        bmi = round(weight / (height ** 2), 2)
        category = classify_bmi(bmi)
        self.result_var.set(f"BMI: {bmi} — {category}")
        save_record(username, weight, height, bmi, category)
        self.refresh_users()

    def plot_trend(self):
        username = self.username_var.get().strip()
        if not username:
            messagebox.showerror("Missing user", "Select a username first.")
            return
        rows = get_history(username)
        if not rows:
            messagebox.showinfo("No data", f"No history found for '{username}' yet.")
            return

        bmis = [r[0] for r in rows]
        dates = [r[1][:16].replace("T", " ") for r in rows]

        self.ax.clear()
        self.ax.plot(range(len(bmis)), bmis, marker="o", color="#2b7de9")
        self.ax.set_xticks(range(len(bmis)))
        self.ax.set_xticklabels(dates, rotation=45, ha="right", fontsize=7)
        self.ax.set_ylabel("BMI")
        self.ax.set_title(f"BMI trend for {username}")
        self.ax.axhline(18.5, color="gray", linestyle="--", linewidth=0.7)
        self.ax.axhline(25, color="gray", linestyle="--", linewidth=0.7)
        self.ax.axhline(30, color="gray", linestyle="--", linewidth=0.7)
        self.figure.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = BMIApp(root)
    root.mainloop()
