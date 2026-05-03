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


def json_error(message, status_code=400):
    response = jsonify({"error": message})
    response.status_code = status_code
    return response


def get_request_json():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def build_classification_payload(result):
    payload = asdict(result)
    leak_matches = payload.pop("leak_matches", [])
    payload["compromised"] = bool(leak_matches)
    payload["leak_match_count"] = len(leak_matches)
    return payload


def validate_letters_and_spaces(data, field_name):
    value = data.get(field_name, "")
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    value = value.strip()
    if len(value) > WORD_MAX_LENGTH:
        raise ValueError(f"{field_name} must be 40 characters or fewer")
    if not value or not all(char.isalpha() or char == " " for char in value):
        raise ValueError(f"{field_name} must contain letters only")
    return value


def validate_letters_only(data, field_name):
    value = data.get(field_name, "")
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    value = value.strip()
    if len(value) > WORD_MAX_LENGTH:
        raise ValueError(f"{field_name} must be 40 characters or fewer")
    if not value or not value.isalpha():
        raise ValueError(f"{field_name} must contain letters only")
    return value


def _validate_digits(data, field_name):
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
    data = get_request_json()
    password = data.get("password", "")

    if not isinstance(password, str) or not password:
        return json_error("password is required")
    if len(password) > PASSWORD_MAX_LENGTH:
        return json_error("password must be 256 characters or fewer")

    result = classify_password(
        password,
        check_leaks=bool(data.get("check_leaks", True)),
    )
    return jsonify(build_classification_payload(result))


@app.post("/generate")
def generate():
    data = get_request_json()

    try:
        password = generate_password(
            length=int(data.get("length", 16)),
            use_upper=bool(data.get("use_upper", True)),
            use_lower=bool(data.get("use_lower", True)),
            use_digits=bool(data.get("use_digits", True)),
            use_symbols=bool(data.get("use_symbols", True)),
        )
    except (TypeError, ValueError) as e:
        return json_error(str(e))

    classification = classify_password(password)

    return jsonify({
        "password": password,
        "classification": build_classification_payload(classification),
    })


@app.post("/generate-personalized")
def generate_personalized():
    data = get_request_json()

    try:
        fruit = validate_letters_only(data, "fruit")
        street = validate_letters_and_spaces(data, "street")
        number = _validate_digits(data, "number")
        password = generate_personalized_password(fruit, street, number)
    except (TypeError, ValueError) as e:
        return json_error(str(e))

    classification = classify_password(password)

    return jsonify({
        "password": password,
        "classification": build_classification_payload(classification),
    })


if __name__ == "__main__":
    app.run(debug=True)
