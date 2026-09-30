"""
PROJECT 4: ADVANCED WEATHER APP
-----------------------------------
Features:
- Tkinter GUI with city/ZIP search
- Current conditions: temperature, humidity, wind speed, description
- 5-day / 3-hour forecast summarized into a daily outlook
- Celsius <-> Fahrenheit unit toggle
- Basic weather icon indicator (emoji-based, no external image downloads)
- Robust error handling for bad input / network issues

SETUP:
    pip install requests

You need a free API key from https://openweathermap.org/api
Set WEATHER_API_KEY below.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
import requests

try:
    # pyrefly: ignore [missing-import]
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

WEATHER_EMOJI = {
    "Clear": "☀️",
    "Clouds": "☁️",
    "Rain": "🌧️",
    "Drizzle": "🌦️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Mist": "🌫️",
    "Fog": "🌫️",
    "Haze": "🌫️",
}


def c_to_f(celsius):
    return celsius * 9 / 5 + 32


class WeatherApp:
    def __init__(self, root):
        self.root = root
        root.title("Advanced Weather App")
        root.geometry("480x560")
        self.unit_celsius = tk.BooleanVar(value=True)
        self.last_data_celsius = {}  # cache last fetched values in Celsius

        top = ttk.Frame(root, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="City or ZIP code:").pack(side="left")
        self.location_var = tk.StringVar()
        entry = ttk.Entry(top, textvariable=self.location_var)
        entry.pack(side="left", fill="x", expand=True, padx=6)
        entry.bind("<Return>", lambda e: self.fetch_weather())

        ttk.Button(top, text="Search", command=self.fetch_weather).pack(side="left")

        unit_frame = ttk.Frame(root, padding=(10, 0))
        unit_frame.pack(fill="x")
        ttk.Radiobutton(unit_frame, text="°C", variable=self.unit_celsius, value=True,
                         command=self.refresh_display).pack(side="left")
        ttk.Radiobutton(unit_frame, text="°F", variable=self.unit_celsius, value=False,
                         command=self.refresh_display).pack(side="left")

        self.current_frame = ttk.LabelFrame(root, text="Current Conditions", padding=12)
        self.current_frame.pack(fill="x", padx=10, pady=10)

        self.icon_label = ttk.Label(self.current_frame, text="—", font=("Segoe UI", 40))
        self.icon_label.pack()
        self.temp_label = ttk.Label(self.current_frame, text="", font=("Segoe UI", 22, "bold"))
        self.temp_label.pack()
        self.desc_label = ttk.Label(self.current_frame, text="")
        self.desc_label.pack()
        self.details_label = ttk.Label(self.current_frame, text="", justify="left")
        self.details_label.pack(pady=6)

        self.forecast_frame = ttk.LabelFrame(root, text="5-Day Outlook", padding=12)
        self.forecast_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.forecast_text = tk.Text(self.forecast_frame, height=12, wrap="word", state="disabled")
        self.forecast_text.pack(fill="both", expand=True)

        if not WEATHER_API_KEY:
            self.desc_label.config(text="⚠ Set WEATHER_API_KEY in .env file to enable live data.")

    def fetch_weather(self):
        location = self.location_var.get().strip()
        if not location:
            messagebox.showerror("Missing location", "Enter a city name or ZIP code.")
            return
        if not WEATHER_API_KEY:
            messagebox.showerror("API key missing", "Set WEATHER_API_KEY in your .env file or environment.")
            return

        try:
            params = {"q": location, "appid": WEATHER_API_KEY, "units": "metric"}
            r = requests.get(CURRENT_URL, params=params, timeout=8)
            data = r.json()
            if str(data.get("cod")) != "200":
                messagebox.showerror("Not found", data.get("message", "Location not found."))
                return

            self.last_data_celsius = {
                "temp": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "wind": data["wind"]["speed"],
                "desc": data["weather"][0]["description"].title(),
                "main": data["weather"][0]["main"],
                "city": data["name"],
            }
            self.refresh_display()
            self.fetch_forecast(location)

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Network error", f"Could not reach weather service:\n{e}")
        except (KeyError, ValueError):
            messagebox.showerror("Error", "Unexpected response from weather service.")

    def refresh_display(self):
        d = self.last_data_celsius
        if not d:
            return
        celsius = self.unit_celsius.get()
        temp = d["temp"] if celsius else c_to_f(d["temp"])
        feels = d["feels_like"] if celsius else c_to_f(d["feels_like"])
        unit = "°C" if celsius else "°F"

        self.icon_label.config(text=WEATHER_EMOJI.get(d["main"], "🌡️"))
        self.temp_label.config(text=f"{temp:.1f}{unit}  in {d['city']}")
        self.desc_label.config(text=d["desc"])
        self.details_label.config(
            text=f"Feels like: {feels:.1f}{unit}\nHumidity: {d['humidity']}%\nWind: {d['wind']} m/s"
        )

    def fetch_forecast(self, location):
        try:
            params = {"q": location, "appid": WEATHER_API_KEY, "units": "metric"}
            r = requests.get(FORECAST_URL, params=params, timeout=8)
            data = r.json()
            if str(data.get("cod")) != "200":
                return

            # Group forecast entries by date, average temp, take midday description
            daily = {}
            for entry in data["list"]:
                date = entry["dt_txt"].split(" ")[0]
                daily.setdefault(date, []).append(entry)

            lines = []
            for date, entries in list(daily.items())[:5]:
                temps = [e["main"]["temp"] for e in entries]
                avg_temp = sum(temps) / len(temps)
                midday = min(entries, key=lambda e: abs(int(e["dt_txt"][11:13]) - 12))
                desc = midday["weather"][0]["description"].title()
                if not self.unit_celsius.get():
                    avg_temp = c_to_f(avg_temp)
                unit = "°C" if self.unit_celsius.get() else "°F"
                emoji = WEATHER_EMOJI.get(midday["weather"][0]["main"], "🌡️")
                lines.append(f"{date}: {emoji} {avg_temp:.1f}{unit} — {desc}")

            self.forecast_text.configure(state="normal")
            self.forecast_text.delete("1.0", tk.END)
            self.forecast_text.insert(tk.END, "\n".join(lines))
            self.forecast_text.configure(state="disabled")

        except requests.exceptions.RequestException:
            pass  # current conditions already shown; forecast is best-effort


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
