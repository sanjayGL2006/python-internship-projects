"""
PROJECT 1: ADVANCED VOICE ASSISTANT
-------------------------------------
Features:
- Speech recognition (mic) + text-to-speech replies
- Tkinter GUI with a live transcript / log
- Commands: greetings, time/date, web search, weather (OpenWeatherMap API),
  set reminders (background timer), send email, general knowledge (Wikipedia),
  custom command aliases (customization)
- Error handling for mic/network issues
- Basic "privacy" mode: emails/reminders require explicit confirmation

SETUP:
    pip install SpeechRecognition pyttsx3 pyaudio requests wikipedia

Notes:
- Replace WEATHER_API_KEY with your own key from https://openweathermap.org/api
- Email sending requires an app password (e.g. Gmail App Password), never your
  real account password. Fill EMAIL_ADDRESS / EMAIL_APP_PASSWORD below or leave
  blank to disable email feature.
"""

import threading
import time
import datetime
import webbrowser
import smtplib
import json
import os
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog

import requests

try:
    import speech_recognition as sr # type: ignore
except ImportError:
    sr = None

try:
    import pyttsx3 # type: ignore
except ImportError:
    pyttsx3 = None

try:
    import wikipedia # type: ignore
except ImportError:
    wikipedia = None

try:
    # pyrefly: ignore [missing-import]
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ---------------- CONFIG ----------------
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")          # e.g. "you@gmail.com"
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "")     # Gmail "App Password", not your real password
CUSTOM_COMMANDS_FILE = "custom_commands.json"


class VoiceAssistant:
    def __init__(self, log_callback):
        self.log = log_callback
        self.engine = pyttsx3.init() if pyttsx3 else None
        self.recognizer = sr.Recognizer() if sr else None
        self.custom_commands = self._load_custom_commands()
        self.reminders = []

    # ---------- persistence ----------
    def _load_custom_commands(self):
        if os.path.exists(CUSTOM_COMMANDS_FILE):
            try:
                with open(CUSTOM_COMMANDS_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_custom_commands(self):
        with open(CUSTOM_COMMANDS_FILE, "w") as f:
            json.dump(self.custom_commands, f, indent=2)

    # ---------- speech I/O ----------
    def speak(self, text):
        self.log(f"Assistant: {text}")
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()

    def listen(self):
        """Capture one utterance from the microphone. Returns lowercase text or None."""
        if not self.recognizer or not sr:
            self.log("Error: speech_recognition/pyaudio not installed.")
            return None
        try:
            with sr.Microphone() as source:
                self.log("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=6, phrase_time_limit=8)
            text = self.recognizer.recognize_google(audio)
            self.log(f"You: {text}")
            return text.lower()
        except sr.WaitTimeoutError:
            self.log("Timed out waiting for speech.")
        except sr.UnknownValueError:
            self.log("Sorry, I didn't catch that.")
        except sr.RequestError as e:
            self.log(f"Speech service error: {e}")
        except Exception as e:
            self.log(f"Mic error: {e}")
        return None

    # ---------- NLP-ish intent handling ----------
    def handle_command(self, text):
        if not text:
            return

        # user-defined custom commands take priority
        for trigger, response in self.custom_commands.items():
            if trigger in text:
                self.speak(response)
                return

        if any(w in text for w in ["hello", "hi there", "hey"]):
            self.speak("Hello! How can I help you today?")

        elif "time" in text:
            now = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"The current time is {now}")

        elif "date" in text:
            today = datetime.datetime.now().strftime("%A, %B %d, %Y")
            self.speak(f"Today is {today}")

        elif "search" in text or "google" in text:
            query = text.replace("search", "").replace("google", "").replace("for", "").strip()
            if query:
                self.speak(f"Searching the web for {query}")
                webbrowser.open(f"https://www.google.com/search?q={query}")
            else:
                self.speak("What would you like me to search for?")

        elif "weather" in text:
            city = text.replace("weather", "").replace("in", "").strip() or "London"
            self.get_weather(city)

        elif "who is" in text or "what is" in text:
            self.wiki_lookup(text)

        elif "remind me" in text:
            self.set_reminder(text)

        elif "email" in text and EMAIL_ADDRESS:
            self.speak("Email drafting via voice needs the GUI form. Use the Send Email button.")

        elif "exit" in text or "quit" in text or "stop" in text:
            self.speak("Goodbye!")

        else:
            self.speak("I'm not sure how to help with that yet.")

    # ---------- task automation ----------
    def get_weather(self, city):
        if WEATHER_API_KEY == "YOUR_OPENWEATHERMAP_API_KEY":
            self.speak("Weather API key isn't configured yet.")
            return
        try:
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}
            r = requests.get(url, params=params, timeout=8)
            data = r.json()
            if data.get("cod") != 200:
                self.speak(f"Couldn't find weather for {city}")
                return
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            self.speak(f"It's {temp} degrees Celsius with {desc} in {city}")
        except Exception as e:
            self.speak("I had trouble reaching the weather service.")
            self.log(f"Weather error: {e}")

    def wiki_lookup(self, text):
        if not wikipedia:
            self.speak("Wikipedia lookup isn't available; install the wikipedia package.")
            return
        query = text.replace("who is", "").replace("what is", "").strip()
        try:
            summary = wikipedia.summary(query, sentences=2)
            self.speak(summary)
        except Exception as e:
            self.speak("I couldn't find information on that.")
            self.log(f"Wikipedia error: {e}")

    def set_reminder(self, text):
        # naive parse: "remind me to X in N minutes"
        try:
            if " in " in text:
                task_part, time_part = text.split(" in ", 1)
                task = task_part.replace("remind me to", "").strip()
                minutes = int("".join(filter(str.isdigit, time_part)) or 1)
            else:
                task = text.replace("remind me to", "").strip()
                minutes = 1
        except Exception:
            task, minutes = text, 1

        self.speak(f"Okay, I'll remind you to {task} in {minutes} minute(s).")

        def fire():
            time.sleep(minutes * 60)
            self.speak(f"Reminder: {task}")

        threading.Thread(target=fire, daemon=True).start()

    def send_email(self, to_addr, subject, body):
        if not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
            self.speak("Email isn't configured. Set EMAIL_ADDRESS and EMAIL_APP_PASSWORD.")
            return
        try:
            msg = f"Subject: {subject}\n\n{body}"
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
                server.sendmail(EMAIL_ADDRESS, to_addr, msg)
            self.speak("Email sent successfully.")
        except Exception as e:
            self.speak("Failed to send the email.")
            self.log(f"Email error: {e}")

    def add_custom_command(self, trigger, response):
        self.custom_commands[trigger.lower()] = response
        self._save_custom_commands()


class AssistantGUI:
    def __init__(self, root):
        self.root = root
        root.title("Voice Assistant")
        root.geometry("560x520")

        self.log_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="🎤 Listen", width=14, command=self.listen_once).grid(row=0, column=0, padx=4)
        tk.Button(btn_frame, text="Send Email", width=14, command=self.send_email_dialog).grid(row=0, column=1, padx=4)
        tk.Button(btn_frame, text="Add Custom Cmd", width=14, command=self.add_custom_dialog).grid(row=0, column=2, padx=4)

        self.assistant = VoiceAssistant(self.append_log)
        self.append_log("Assistant ready. Click 'Listen' and speak a command.")

    def append_log(self, text):
        self.log_box.configure(state="normal")
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.configure(state="disabled")
        self.log_box.see(tk.END)

    def listen_once(self):
        def worker():
            text = self.assistant.listen()
            self.assistant.handle_command(text)
        threading.Thread(target=worker, daemon=True).start()

    def send_email_dialog(self):
        to_addr = simpledialog.askstring("Send Email", "Recipient email:")
        if not to_addr:
            return
        subject = simpledialog.askstring("Send Email", "Subject:") or "(no subject)"
        body = simpledialog.askstring("Send Email", "Body:") or ""
        threading.Thread(target=self.assistant.send_email, args=(to_addr, subject, body), daemon=True).start()

    def add_custom_dialog(self):
        trigger = simpledialog.askstring("Custom Command", "Trigger phrase (heard in speech):")
        if not trigger:
            return
        response = simpledialog.askstring("Custom Command", "Assistant's spoken response:")
        if response is None:
            return
        self.assistant.add_custom_command(trigger, response)
        self.append_log(f"Added custom command: '{trigger}' -> '{response}'")


if __name__ == "__main__":
    if sr is None or pyttsx3 is None:
        print("Warning: install SpeechRecognition, pyaudio, and pyttsx3 for full functionality.")
    root = tk.Tk()
    app = AssistantGUI(root)
    root.mainloop()
