# 🐍 Python Internship Projects

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Security](https://img.shields.io/badge/Security-GitGuardian--Protected-brightgreen.svg)

A curated collection of practical Python applications and GUI desktop tools developed as part of the Python Internship. This repository includes desktop tools, voice assistants, network socket chat applications, data visualization utilities, and live web API integrations.

---

## 🚀 Projects Included

### 1. 🎙️ Advanced Voice Assistant (`1_voice_assistant.py`)
An interactive voice-enabled AI assistant built with Speech Recognition and Text-to-Speech (TTS) capabilities.
* **Key Features:**
  * Voice recognition using microphone input with live GUI transcript logging.
  * Voice and text responses via `pyttsx3`.
  * Web search, current weather integration, Wikipedia knowledge querying, and custom user command aliases.
  * Reminder scheduler with background timer execution.
  * Email sending functionality with user confirmation.

### 2. ⚖️ Advanced BMI Calculator (`2_bmi_calculator.py`)
A graphical user interface application built with Tkinter for calculating, tracking, and analyzing Body Mass Index (BMI).
* **Key Features:**
  * Accurate metric and imperial unit conversions.
  * Medical BMI categories (Underweight, Normal, Overweight, Obese).
  * SQLite database integration (`bmi_data.db`) for storing historical logs per user.
  * Historical trend analysis and visual chart rendering using `matplotlib`.

### 3. 🔐 Advanced Random Password Generator (`3_password_generator.py`)
A custom password generator and security evaluation tool designed for password safety.
* **Key Features:**
  * Customizable password length and character combinations (uppercase, lowercase, numbers, special symbols).
  * Enforced character inclusion rules (e.g., must contain at least one digit or symbol).
  * Built-in password strength metric algorithm (Weak, Fair, Good, Strong).
  * Clipboard integration to quickly copy generated passwords.

### 4. 🌤️ Advanced Weather Application (`4_weather_app.py`)
A real-time weather information dashboard powered by the OpenWeatherMap API.
* **Key Features:**
  * Search weather by city name or ZIP code.
  * Display current weather parameters: temperature, feels-like temperature, humidity, wind speed, and condition description.
  * 5-day / 3-hour weather outlook summarized into a daily weather forecast.
  * Unit toggle between Celsius (°C) and Fahrenheit (°F).
  * Safe environment-variable handling via `.env`.

### 5. 💬 End-to-End Encrypted Chat Application (`5_chat_app_server.py` & `5_chat_app_client.py`)
A real-time, multi-user socket chat server and client application.
* **Key Features:**
  * Multi-threaded TCP socket architecture supporting concurrent client connections.
  * End-to-End Encryption (E2EE) powered by Python's `cryptography` (Fernet symmetric key encryption).
  * User registration and authentication mechanism.
  * Dedicated chat rooms, private messaging, and user broadcast support.

---

## 📁 Repository Structure

```text
python-internship-projects/
├── 1_voice_assistant.py       # Voice Assistant application
├── 2_bmi_calculator.py        # GUI BMI Calculator & Tracker
├── 3_password_generator.py    # Password Generator & Strength Checker
├── 4_weather_app.py           # OpenWeatherMap Weather GUI App
├── 5_chat_app_server.py       # Multi-Client Encrypted Chat Server
├── 5_chat_app_client.py       # Encrypted Chat Client GUI
├── .env.example               # Template for required environment variables
├── .gitignore                 # Prevents sensitive files & binaries from commit
├── requirements.txt           # Project dependencies
└── README.md                  # Project Documentation
```

---

## 🛠️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/sanjayGL2006/python-internship-projects.git
cd python-internship-projects
```

### 2. Create a Virtual Environment (Optional but Recommended)
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to create your own `.env` file:
```bash
cp .env.example .env
```
Open `.env` and configure your API keys:
```env
WEATHER_API_KEY=your_actual_openweathermap_api_key
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_APP_PASSWORD=your_app_password
```

> ⚠️ **Note:** Never commit your `.env` file or API keys to public repositories. `.env` is listed in `.gitignore`.

---

## 🏃 Running the Applications

Run any project directly using Python:

```bash
# 1. Voice Assistant
python 1_voice_assistant.py

# 2. BMI Calculator
python 2_bmi_calculator.py

# 3. Password Generator
python 3_password_generator.py

# 4. Weather App
python 4_weather_app.py

# 5. Encrypted Chat Application
# Step 1: Start the server
python 5_chat_app_server.py

# Step 2: Copy generated key.key file to client folder (if needed) and run client:
python 5_chat_app_client.py
```

---

## 🔒 Security & Best Practices

* **No Hardcoded Secrets:** All API keys and credentials are strictly retrieved via environment variables using `python-dotenv`.
* **GitGuardian Monitored:** Repository history is audited to prevent accidental leaks of tokens or sensitive keys.
* **Database Isolation:** Runtime databases (e.g. `bmi_data.db`) and encryption keys (`key.key`) are automatically excluded from version control via `.gitignore`.

---

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
