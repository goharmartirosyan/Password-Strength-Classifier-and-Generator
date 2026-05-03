from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path


DEFAULT_PLAIN_FOLDER = Path(__file__).resolve().parents[1] / "data"


@dataclass(frozen=True)
class LeakMatch:
    database: str
    line_number: int
    leaked_password: str
    match_type: str


def _normalize(value: str, case_sensitive: bool) -> str:
    return value if case_sensitive else value.casefold()


def _check_file(
    file_path: Path,
    password: str,
    *,
    case_sensitive: bool,
    min_substring_length: int,
    max_matches_per_file: int,
) -> list[LeakMatch]:
    matches: list[LeakMatch] = []
    exact_match: LeakMatch | None = None
    password_to_check = _normalize(password, case_sensitive)

    with file_path.open("r", encoding="utf-8", errors="ignore") as infile:
        for line_number, line in enumerate(infile, start=1):
            leaked_password = line.strip()
            if not leaked_password:
                continue

            leaked_to_check = _normalize(leaked_password, case_sensitive)
            match_type = None

            if password_to_check == leaked_to_check:
                exact_match = LeakMatch(
                    database=file_path.name,
                    line_number=line_number,
                    leaked_password=leaked_password,
                    match_type="exact",
                )
                break
            elif (
                len(leaked_to_check) >= min_substring_length
                and leaked_to_check in password_to_check
            ):
                match_type = "inside_passphrase"

            if match_type:
                if len(matches) < max_matches_per_file:
                    matches.append(
                        LeakMatch(
                            database=file_path.name,
                            line_number=line_number,
                            leaked_password=leaked_password,
                            match_type=match_type,
                        )
                    )

    if exact_match:
        matches.insert(0, exact_match)
    return matches


def check_password_in_plain_databases(
    password: str,
    *,
    plain_folder: Path | str = DEFAULT_PLAIN_FOLDER,
    case_sensitive: bool = False,
    min_substring_length: int = 4,
    max_matches_per_file: int = 5,
    workers: int | None = None,
) -> list[LeakMatch]:
    """
    Checks all plain-text password databases in parallel.

    It reports exact matches and leaked passwords that appear inside a longer
    password/passphrase. Very short substring matches are ignored by default to
    avoid noisy hits like "12" appearing inside a stronger password.
    """
    password = password.strip()
    if not password:
        return []

    plain_folder = Path(plain_folder)
    database_files = sorted(plain_folder.glob("*.txt"))
    if not database_files:
        return []

    with ThreadPoolExecutor(max_workers=workers or len(database_files)) as executor:
        futures = [
            executor.submit(
                _check_file,
                database_file,
                password,
                case_sensitive=case_sensitive,
                min_substring_length=min_substring_length,
                max_matches_per_file=max_matches_per_file,
            )
            for database_file in database_files
        ]

        matches: list[LeakMatch] = []
        for future in as_completed(futures):
            matches.extend(future.result())

    return sorted(matches, key=lambda match: (match.database, match.line_number))


def is_password_compromised(password: str, **kwargs) -> bool:
    return bool(check_password_in_plain_databases(password, **kwargs))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check a password/passphrase against plain leak databases."
    )
    parser.add_argument("password", help="Password or passphrase to check.")
    parser.add_argument(
        "--plain-folder",
        type=Path,
        default=DEFAULT_PLAIN_FOLDER,
        help="Folder containing plain .txt password databases.",
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="Match with exact character casing.",
    )
    parser.add_argument(
        "--min-substring-length",
        type=int,
        default=4,
        help="Minimum leaked-password length for inside-passphrase matches.",
    )
    parser.add_argument(
        "--max-matches-per-file",
        type=int,
        default=5,
        help="Stop after this many matches from each database file.",
    )
    args = parser.parse_args()

    matches = check_password_in_plain_databases(
        args.password,
        plain_folder=args.plain_folder,
        case_sensitive=args.case_sensitive,
        min_substring_length=args.min_substring_length,
        max_matches_per_file=args.max_matches_per_file,
    )

    if not matches:
        print("No matches found in plain databases.")
        return

    print(f"Found {len(matches)} match(es):")
    for match in matches:
        print(
            f"- {match.database}:{match.line_number} "
            f"[{match.match_type}] {match.leaked_password}"
        )


if __name__ == "__main__":
    main()
