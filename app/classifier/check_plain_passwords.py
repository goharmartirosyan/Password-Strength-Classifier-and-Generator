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


def normalize(value, case_sensitive):
    return value if case_sensitive else value.casefold()


def check_single_file(file_path, password, case_sensitive=False, min_substring_length=4, max_matches_per_file=5):
    matches = []
    exact_match = None
    password_to_check = normalize(password, case_sensitive)

    with file_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line_number, line in enumerate(f, start=1):
            leaked_password = line.strip()
            if not leaked_password:
                continue

            leaked_to_check = normalize(leaked_password, case_sensitive)
            match_type = None

            if password_to_check == leaked_to_check:
                exact_match = LeakMatch(
                    database=file_path.name,
                    line_number=line_number,
                    leaked_password=leaked_password,
                    match_type="exact",
                )
                break
            elif len(leaked_to_check) >= min_substring_length and leaked_to_check in password_to_check:
                match_type = "inside_passphrase"

            if match_type:
                if len(matches) < max_matches_per_file:
                    matches.append(LeakMatch(
                        database=file_path.name,
                        line_number=line_number,
                        leaked_password=leaked_password,
                        match_type=match_type,
                    ))

    if exact_match:
        matches.insert(0, exact_match)
    return matches


def check_password_in_plain_databases(
    password,
    plain_folder=DEFAULT_PLAIN_FOLDER,
    case_sensitive=False,
    min_substring_length=4,
    max_matches_per_file=5,
    workers=None,
):
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
                check_single_file,
                db_file,
                password,
                case_sensitive,
                min_substring_length,
                max_matches_per_file,
            )
            for db_file in database_files
        ]

        matches = []
        for future in as_completed(futures):
            matches.extend(future.result())

    return sorted(matches, key=lambda m: (m.database, m.line_number))


def is_password_compromised(password, **kwargs):
    return bool(check_password_in_plain_databases(password, **kwargs))


def main():
    parser = argparse.ArgumentParser(description="Check a password against leak databases.")
    parser.add_argument("password", help="Password to check.")
    parser.add_argument("--plain-folder", type=Path, default=DEFAULT_PLAIN_FOLDER)
    parser.add_argument("--case-sensitive", action="store_true")
    parser.add_argument("--min-substring-length", type=int, default=4)
    parser.add_argument("--max-matches-per-file", type=int, default=5)
    args = parser.parse_args()

    matches = check_password_in_plain_databases(
        args.password,
        plain_folder=args.plain_folder,
        case_sensitive=args.case_sensitive,
        min_substring_length=args.min_substring_length,
        max_matches_per_file=args.max_matches_per_file,
    )

    if not matches:
        print("No matches found.")
        return

    print(f"Found {len(matches)} match(es):")
    for m in matches:
        print(f"- {m.database}:{m.line_number} [{m.match_type}] {m.leaked_password}")


if __name__ == "__main__":
    main()
