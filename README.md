# Password Suite

A web application for classifying password strength and generating secure passwords.

## Features

- **Classifier** — analyzes a password and returns a strength score, entropy, and suggestions for improvement
- **Random Generator** — generates a secure random password with customizable length and character types (uppercase, lowercase, digits, symbols)
- **Personalized Generator** — generates a memorable password based on a fruit, a street name, and a number
- **Reuse Detection** — checks passwords against local password lists and warns when a password looks reused or already exposed

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

3. Install the required package:
   ```
   pip3 install -r requirements.txt
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

## How Strength Is Measured

The classifier combines several checks:

- password length
- character variety: lowercase, uppercase, digits, and symbols
- estimated entropy
- whether the password appears in local password lists
- repeated characters and common patterns such as `1234`, `qwerty`, or `password`

The entropy value is an estimate based on password length and the character groups used. It is useful as a signal, but it is not perfect because human-created passwords often follow patterns.

## Privacy Note

This project is intended to run locally. Passwords are checked on your own machine and are not sent to an external service.

The web API does not return raw leak-match details. It only returns whether a password appears compromised and how many matches were found.

## Limitations

- The strength score is rule-based, so it may not catch every weak human pattern.
- The local password lists are only as complete as the files placed in `app/data`.
- This is a learning/project tool, not a replacement for a professional password manager or security audit.











