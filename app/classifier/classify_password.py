import argparse
import math
import re
from dataclasses import dataclass
from pathlib import Path

try:
    from check_plain_passwords import LeakMatch, check_password_in_plain_databases
except ImportError:
    from app.classifier.check_plain_passwords import LeakMatch, check_password_in_plain_databases


@dataclass(frozen=True)
class PasswordClassification:
    label: str
    score: int
    entropy: float
    length: int
    character_types: list
    missing_character_types: list
    leak_matches: list
    reasons: list
    suggestions: list


COMMON_PATTERNS = [
    "1234", "12345", "123456",
    "abcd", "abcdef",
    "qwerty", "asdf", "zxcv",
    "password", "passw0rd", "p@ssword", "p@ssw0rd",
    "admin", "letmein", "welcome",
]


def get_character_types(password):
    checks = [
        ("lowercase", r"[a-z]"),
        ("uppercase", r"[A-Z]"),
        ("digits", r"\d"),
        ("symbols", r"[^a-zA-Z0-9]"),
    ]
    present = [name for name, pattern in checks if re.search(pattern, password)]
    missing = [name for name, pattern in checks if not re.search(pattern, password)]
    return present, missing


def calc_entropy(password, character_types):
    pool = 0
    if "lowercase" in character_types:
        pool += 26
    if "uppercase" in character_types:
        pool += 26
    if "digits" in character_types:
        pool += 10
    if "symbols" in character_types:
        pool += 32
    if not password or pool == 0:
        return 0.0
    return len(password) * math.log2(pool)


def get_label(score):
    if score >= 90:
        return "perfect"
    if score >= 70:
        return "good"
    if score >= 50:
        return "normal"
    if score >= 30:
        return "bad"
    return "very bad"


def has_repeated_chars(password):
    return re.search(r"(.)\1{2,}", password) is not None


def has_common_pattern(password):
    lowered = password.casefold()
    return any(p in lowered for p in COMMON_PATTERNS)


def get_suggestions(password, length, missing_character_types, entropy, leak_matches):
    suggestions = []

    if length < 12:
        suggestions.append("Make it at least 12 characters")
    if "uppercase" in missing_character_types:
        suggestions.append("Add uppercase letters")
    if "lowercase" in missing_character_types:
        suggestions.append("Add lowercase letters")
    if "digits" in missing_character_types:
        suggestions.append("Add numbers")
    if "symbols" in missing_character_types:
        suggestions.append("Add symbols")
    if entropy < 45 and length > 0:
        suggestions.append("Use a longer passphrase or more varied characters")
    if leak_matches:
        suggestions.append("Avoid reusing common passwords")
    if has_repeated_chars(password):
        suggestions.append("Avoid repeated characters")
    if has_common_pattern(password):
        suggestions.append("Avoid common words or sequences like password, 1234, or qwerty")
    if not suggestions:
        suggestions.append("This password already follows the main strength guidelines")

    return suggestions


def classify_password(password, plain_folder=None, check_leaks=True):
    password = password.strip()
    character_types, missing_character_types = get_character_types(password)
    entropy = calc_entropy(password, character_types)

    if check_leaks and plain_folder is not None:
        leak_matches = check_password_in_plain_databases(password, plain_folder=plain_folder, max_matches_per_file=3)
    elif check_leaks:
        leak_matches = check_password_in_plain_databases(password, max_matches_per_file=3)
    else:
        leak_matches = []

    reasons = []
    score = 0
    length = len(password)

    if length >= 16:
        score += 35
        reasons.append("long password")
    elif length >= 12:
        score += 28
        reasons.append("good length")
    elif length >= 8:
        score += 18
        reasons.append("acceptable length")
    elif length > 0:
        score += 5
        reasons.append("too short")
    else:
        reasons.append("empty password")

    score += len(character_types) * 10
    if len(character_types) >= 4:
        reasons.append("uses lowercase, uppercase, digits, and symbols")
    elif len(character_types) >= 3:
        reasons.append("uses several character types")
    else:
        reasons.append("uses too few character types")

    if entropy >= 100:
        score += 25
        reasons.append("very high entropy")
    elif entropy >= 70:
        score += 20
        reasons.append("high entropy")
    elif entropy >= 45:
        score += 12
        reasons.append("moderate entropy")
    elif entropy > 0:
        score += 3
        reasons.append("low entropy")

    exact_leak = any(m.match_type == "exact" for m in leak_matches)
    inside_leak = any(m.match_type == "inside_passphrase" for m in leak_matches)

    if exact_leak:
        score = min(score, 20)
        reasons.append("exact password was found in a leak database")
    elif inside_leak:
        score = min(score, 45)
        reasons.append("contains a leaked password inside it")

    score = max(0, min(100, score))
    suggestions = get_suggestions(password, length, missing_character_types, entropy, leak_matches)

    return PasswordClassification(
        label=get_label(score),
        score=score,
        entropy=round(entropy, 2),
        length=length,
        character_types=character_types,
        missing_character_types=missing_character_types,
        leak_matches=leak_matches,
        reasons=reasons,
        suggestions=suggestions,
    )


def main():
    parser = argparse.ArgumentParser(description="Classify password strength.")
    parser.add_argument("password", help="Password to classify.")
    parser.add_argument("--plain-folder", type=Path, default=None)
    parser.add_argument("--skip-leaks", action="store_true")
    args = parser.parse_args()

    result = classify_password(
        args.password,
        plain_folder=args.plain_folder,
        check_leaks=not args.skip_leaks,
    )

    print(f"Classification: {result.label}")
    print(f"Score: {result.score}/100")
    print(f"Entropy: {result.entropy} bits")
    print(f"Length: {result.length}")
    print(f"Character types: {', '.join(result.character_types) or 'none'}")
    print(f"Missing: {', '.join(result.missing_character_types) or 'none'}")
    print(f"Reasons: {', '.join(result.reasons)}")
    print(f"Suggestions: {', '.join(result.suggestions)}")

    if result.leak_matches:
        print("Leak matches:")
        for m in result.leak_matches:
            print(f"- {m.database}:{m.line_number} [{m.match_type}] {m.leaked_password}")


if __name__ == "__main__":
    main()
