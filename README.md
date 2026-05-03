# Password Suite

A web application for classifying password strength and generating secure passwords.

## Features

- **Classifier** — analyzes a password and returns a strength score, entropy, and suggestions for improvement
- **Random Generator** — generates a secure random password with customizable length and character types (uppercase, lowercase, digits, symbols)
- **Personalized Generator** — generates a memorable password based on a fruit, a street name, and a number
- **Leak Detection** — checks passwords against real-world leaked password databases

## Requirements

- Python 3.9+
- Flask

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/goharmartirosyan/Password-Strength-Classifier-and-Generator.git
   ```

2. Navigate to the project folder:
   ```
   cd Password-Strength-Classifier-and-Generator
   ```

3. Install Flask:
   ```
   pip3 install flask
   ```

## Running the App

```
python3 app/web/api.py
```

Then open your browser and go to:

```
http://127.0.0.1:5000
```

To stop the server, press `Ctrl+C` in the terminal.

## Project Structure

```
app/
├── classifier/
│   ├── classify_password.py        # Password scoring and analysis logic
│   └── check_plain_passwords.py    # Checks password against leak databases
├── generator/
│   ├── password_generator.py       # Random password generator
│   └── password_generator_personalized.py  # Personalized password generator
├── data/
│   └── *.txt                       # Leaked password databases
└── web/
    ├── api.py                      # Flask app and API endpoints
    ├── templates/
    │   └── index.html              # Main page
    └── static/
        ├── style.css               # Styles
        └── script.js               # Frontend logic
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serves the main page |
| POST | `/classify` | Classifies a password |
| POST | `/generate` | Generates a random password |
| POST | `/generate-personalized` | Generates a personalized password |
| GET | `/health` | Health check |
Collapse












