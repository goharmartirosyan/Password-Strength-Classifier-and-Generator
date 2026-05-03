from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path

from flask import Flask, jsonify, render_template, request

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.classifier.classify_password import classify_password
from app.generator.password_generator import generate_password
from app.generator.password_generator_personalized import generate_personalized_password


app = Flask(__name__)

PASSWORD_MAX_LENGTH = 256
WORD_MAX_LENGTH = 40


def _json_error(message: str, status_code: int = 400):
    response = jsonify({"error": message})
    response.status_code = status_code
    return response


def _request_json() -> dict:
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def _classification_payload(result) -> dict:
    payload = asdict(result)
    leak_matches = payload.pop("leak_matches", [])
    payload["compromised"] = bool(leak_matches)
    payload["leak_match_count"] = len(leak_matches)
    return payload


def _letters_value(data: dict, field_name: str) -> str:
    value = data.get(field_name, "")
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")

    value = value.strip()
    if len(value) > WORD_MAX_LENGTH:
        raise ValueError(f"{field_name} must be 40 characters or fewer")
    if not value or not all(char.isalpha() or char == " " for char in value):
        raise ValueError(f"{field_name} must contain letters only")

    return value


def _letters_only_value(data: dict, field_name: str) -> str:
    value = data.get(field_name, "")
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")

    value = value.strip()
    if len(value) > WORD_MAX_LENGTH:
        raise ValueError(f"{field_name} must be 40 characters or fewer")
    if not value or not value.isalpha():
        raise ValueError(f"{field_name} must contain letters only")

    return value


def _digits_value(data: dict, field_name: str) -> str:
    value = data.get(field_name, "")
    if isinstance(value, int):
        value = str(value)
    elif not isinstance(value, str):
        raise ValueError(f"{field_name} must be a number")

    value = value.strip()
    if not value.isdigit():
        raise ValueError(f"{field_name} must contain digits only")

    return value


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/classify")
def classify():
    data = _request_json()
    password = data.get("password", "")

    if not isinstance(password, str) or not password:
        return _json_error("password is required")
    if len(password) > PASSWORD_MAX_LENGTH:
        return _json_error("password must be 256 characters or fewer")

    result = classify_password(
        password,
        check_leaks=bool(data.get("check_leaks", True)),
    )

    return jsonify(_classification_payload(result))


@app.post("/generate")
def generate():
    data = _request_json()

    try:
        password = generate_password(
            length=int(data.get("length", 16)),
            use_upper=bool(data.get("use_upper", True)),
            use_lower=bool(data.get("use_lower", True)),
            use_digits=bool(data.get("use_digits", True)),
            use_symbols=bool(data.get("use_symbols", True)),
        )
    except (TypeError, ValueError) as error:
        return _json_error(str(error))

    classification = classify_password(password)

    return jsonify(
        {
            "password": password,
            "classification": _classification_payload(classification),
        }
    )


@app.post("/generate-personalized")
def generate_personalized():
    data = _request_json()

    try:
        fruit = _letters_only_value(data, "fruit")
        street = _letters_value(data, "street")
        number = _digits_value(data, "number")
        password = generate_personalized_password(
            fruit,
            street,
            number,
        )
    except (TypeError, ValueError) as error:
        return _json_error(str(error))

    classification = classify_password(password)

    return jsonify(
        {
            "password": password,
            "classification": _classification_payload(classification),
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
