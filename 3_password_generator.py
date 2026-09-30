"""
PROJECT 3: ADVANCED RANDOM PASSWORD GENERATOR
-------------------------------------------------
Features:
- Tkinter GUI with sliders/checkboxes for length & character sets
- Security rules: guarantee at least one of each selected character type,
  avoid ambiguous characters (optional), strength meter
- Clipboard integration (copy with one click)
- Customization: exclude specific characters, generate multiple at once

SETUP:
    pip install pyperclip
"""

import random
import string
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import pyperclip
except ImportError:
    pyperclip = None

AMBIGUOUS_CHARS = "il1Lo0O"


def generate_password(length, use_upper, use_lower, use_digits, use_symbols,
                       avoid_ambiguous, exclude_chars):
    pools = []
    if use_upper:
        pools.append(string.ascii_uppercase)
    if use_lower:
        pools.append(string.ascii_lowercase)
    if use_digits:
        pools.append(string.digits)
    if use_symbols:
        pools.append("!@#$%^&*()-_=+[]{};:,.<>?")

    if not pools:
        raise ValueError("Select at least one character type.")

    def clean(pool):
        result = pool
        if avoid_ambiguous:
            result = "".join(c for c in result if c not in AMBIGUOUS_CHARS)
        if exclude_chars:
            result = "".join(c for c in result if c not in exclude_chars)
        return result

    pools = [clean(p) for p in pools]
    pools = [p for p in pools if p]  # drop empty pools after filtering

    if not pools:
        raise ValueError("Filters removed every available character. Loosen restrictions.")

    if length < len(pools):
        raise ValueError(f"Length must be at least {len(pools)} to include every selected type.")

    # Guarantee at least one char from each selected pool (security rule)
    password_chars = [random.choice(p) for p in pools]
    all_chars = "".join(pools)
    password_chars += [random.choice(all_chars) for _ in range(length - len(pools))]
    random.shuffle(password_chars)
    return "".join(password_chars)


def estimate_strength(password):
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in "!@#$%^&*()-_=+[]{};:,.<>?" for c in password):
        score += 1
    labels = ["Very Weak", "Weak", "Fair", "Good", "Strong", "Very Strong", "Excellent"]
    return labels[min(score, len(labels) - 1)]


class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        root.title("Advanced Password Generator")
        root.geometry("480x520")

        frame = ttk.Frame(root, padding=12)
        frame.pack(fill="both", expand=True)

        # Length
        ttk.Label(frame, text="Password length:").grid(row=0, column=0, sticky="w")
        self.length_var = tk.IntVar(value=16)
        length_scale = ttk.Scale(frame, from_=4, to=64, variable=self.length_var,
                                  orient="horizontal", command=self._sync_length_label)
        length_scale.grid(row=0, column=1, sticky="ew", padx=8)
        self.length_label = ttk.Label(frame, text="16")
        self.length_label.grid(row=0, column=2)

        # Char type checkboxes
        self.use_upper = tk.BooleanVar(value=True)
        self.use_lower = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        self.avoid_ambiguous = tk.BooleanVar(value=False)

        ttk.Checkbutton(frame, text="Uppercase (A-Z)", variable=self.use_upper).grid(row=1, column=0, sticky="w", pady=2)
        ttk.Checkbutton(frame, text="Lowercase (a-z)", variable=self.use_lower).grid(row=2, column=0, sticky="w", pady=2)
        ttk.Checkbutton(frame, text="Digits (0-9)", variable=self.use_digits).grid(row=3, column=0, sticky="w", pady=2)
        ttk.Checkbutton(frame, text="Symbols (!@#...)", variable=self.use_symbols).grid(row=4, column=0, sticky="w", pady=2)
        ttk.Checkbutton(frame, text="Avoid ambiguous (l, 1, I, O, 0)", variable=self.avoid_ambiguous).grid(
            row=5, column=0, columnspan=2, sticky="w", pady=2
        )

        # Exclude characters
        ttk.Label(frame, text="Exclude characters:").grid(row=6, column=0, sticky="w", pady=(10, 2))
        self.exclude_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.exclude_var).grid(row=6, column=1, columnspan=2, sticky="ew", pady=(10, 2))

        # How many to generate
        ttk.Label(frame, text="Number of passwords:").grid(row=7, column=0, sticky="w", pady=(10, 2))
        self.count_var = tk.IntVar(value=1)
        ttk.Spinbox(frame, from_=1, to=20, textvariable=self.count_var, width=5).grid(row=7, column=1, sticky="w")

        ttk.Button(frame, text="Generate", command=self.generate).grid(row=8, column=0, columnspan=3, pady=12)

        # Output
        self.output_box = tk.Listbox(frame, height=10)
        self.output_box.grid(row=9, column=0, columnspan=3, sticky="nsew", pady=4)
        frame.rowconfigure(9, weight=1)
        frame.columnconfigure(1, weight=1)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=10, column=0, columnspan=3, pady=6)
        ttk.Button(btn_frame, text="Copy Selected", command=self.copy_selected).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Copy All", command=self.copy_all).pack(side="left", padx=4)

        self.strength_var = tk.StringVar(value="")
        ttk.Label(frame, textvariable=self.strength_var, font=("Segoe UI", 10, "italic")).grid(
            row=11, column=0, columnspan=3, sticky="w"
        )

    def _sync_length_label(self, _event=None):
        self.length_label.config(text=str(self.length_var.get()))

    def generate(self):
        self.output_box.delete(0, tk.END)
        try:
            length = int(self.length_var.get())
            passwords = []
            for _ in range(self.count_var.get()):
                pw = generate_password(
                    length,
                    self.use_upper.get(),
                    self.use_lower.get(),
                    self.use_digits.get(),
                    self.use_symbols.get(),
                    self.avoid_ambiguous.get(),
                    self.exclude_var.get(),
                )
                passwords.append(pw)
                self.output_box.insert(tk.END, pw)
            if passwords:
                self.strength_var.set(f"Strength (last generated): {estimate_strength(passwords[-1])}")
        except ValueError as e:
            messagebox.showerror("Cannot generate password", str(e))

    def copy_selected(self):
        selection = self.output_box.curselection()
        if not selection:
            messagebox.showinfo("Nothing selected", "Click a password in the list first.")
            return
        pw = self.output_box.get(selection[0])
        self._copy(pw)

    def copy_all(self):
        items = self.output_box.get(0, tk.END)
        if not items:
            messagebox.showinfo("Nothing to copy", "Generate passwords first.")
            return
        self._copy("\n".join(items))

    def _copy(self, text):
        if pyperclip:
            pyperclip.copy(text)
            messagebox.showinfo("Copied", "Copied to clipboard.")
        else:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Copied", "Copied to clipboard (fallback method).")


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()
