from __future__ import annotations

import argparse
import math
import re
from dataclasses import dataclass
from pathlib import Path

try:
    from check_plain_passwords import LeakMatch, check_password_in_plain_databases
except ImportError:
    from app.classifier.check_plain_passwords import (
        LeakMatch,
        check_password_in_plain_databases,
    )


@dataclass(frozen=True)
class PasswordClassification:
    label: str
    score: int
    entropy: float
    length: int
    character_types: list[str]
    missing_character_types: list[str]
    leak_matches: list[LeakMatch]
    reasons: list[str]
    suggestions: list[str]


COMMON_PATTERNS = [
    "1234",
    "12345",
    "123456",
    "abcd",
    "abcdef",
    "qwerty",
    "asdf",
    "zxcv",
    "password",
    "passw0rd",
    "p@ssword",
    "p@ssw0rd",
    "admin",
    "letmein",
    "welcome",
]


def _character_type_report(password: str) -> tuple[list[str], list[str]]:
    checks = [
        ("lowercase", r"[a-z]"),
        ("uppercase", r"[A-Z]"),
        ("digits", r"\d"),
        ("symbols", r"[^a-zA-Z0-9]"),
    ]

    present = [name for name, pattern in checks if re.search(pattern, password)]
    missing = [name for name, pattern in checks if not re.search(pattern, password)]
    return present, missing


def _entropy_bits(password: str, character_types: list[str]) -> float:
    pool_size = 0
    if "lowercase" in character_types:
        pool_size += 26
    if "uppercase" in character_types:
        pool_size += 26
    if "digits" in character_types:
        pool_size += 10
    if "symbols" in character_types:
        pool_size += 32

    if not password or pool_size == 0:
        return 0.0

    return len(password) * math.log2(pool_size)


def _label_from_score(score: int) -> str:
    if score >= 90:
        return "perfect"
    if score >= 70:
        return "good"
    if score >= 50:
        return "normal"
    if score >= 30:
        return "bad"
    return "very bad"


def _has_repeated_characters(password: str) -> bool:
    return re.search(r"(.)\1{2,}", password) is not None


def _has_common_pattern(password: str) -> bool:
    lowered = password.casefold()
    return any(pattern in lowered for pattern in COMMON_PATTERNS)


def _password_suggestions(
    password: str,
    *,
    length: int,
    missing_character_types: list[str],
    entropy: float,
    leak_matches: list[LeakMatch],
) -> list[str]:
    suggestions: list[str] = []

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

    if _has_repeated_characters(password):
        suggestions.append("Avoid repeated characters")

    if _has_common_pattern(password):
        suggestions.append("Avoid common words or sequences like password, 1234, or qwerty")

    if not suggestions:
        suggestions.append("This password already follows the main strength guidelines")

    return suggestions


def classify_password(
    password: str,
    *,
    plain_folder: Path | str | None = None,
    check_leaks: bool = True,
) -> PasswordClassification:
    password = password.strip()
    character_types, missing_character_types = _character_type_report(password)
    entropy = _entropy_bits(password, character_types)
    leak_matches = (
        check_password_in_plain_databases(
            password,
            plain_folder=plain_folder,
            max_matches_per_file=3,
        )
        if check_leaks and plain_folder is not None
        else check_password_in_plain_databases(password, max_matches_per_file=3)
        if check_leaks
        else []
    )

    reasons: list[str] = []
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

    exact_leak = any(match.match_type == "exact" for match in leak_matches)
    inside_leak = any(match.match_type == "inside_passphrase" for match in leak_matches)

    if exact_leak:
        score = min(score, 20)
        reasons.append("exact password was found in a leak database")
    elif inside_leak:
        score = min(score, 45)
        reasons.append("contains a leaked password inside it")

    score = max(0, min(100, score))
    suggestions = _password_suggestions(
        password,
        length=length,
        missing_character_types=missing_character_types,
        entropy=entropy,
        leak_matches=leak_matches,
    )

    return PasswordClassification(
        label=_label_from_score(score),
        score=score,
        entropy=round(entropy, 2),
        length=length,
        character_types=character_types,
        missing_character_types=missing_character_types,
        leak_matches=leak_matches,
        reasons=reasons,
        suggestions=suggestions,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify password strength.")
    parser.add_argument("password", help="Password or passphrase to classify.")
    parser.add_argument(
        "--plain-folder",
        type=Path,
        default=None,
        help="Optional folder containing plain .txt password databases.",
    )
    parser.add_argument(
        "--skip-leaks",
        action="store_true",
        help="Do not check local plain-text leak databases.",
    )
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
        for match in result.leak_matches:
            print(
                f"- {match.database}:{match.line_number} "
                f"[{match.match_type}] {match.leaked_password}"
            )


if __name__ == "__main__":
    main()
