import secrets
import string

def generate_password(length=12, use_upper=True, use_lower=True, use_digits=True, use_symbols=True):
    characters = ""
    password = []

    if use_lower:
        characters += string.ascii_lowercase
        password.append(secrets.choice(string.ascii_lowercase))

    if use_upper:
        characters += string.ascii_uppercase
        password.append(secrets.choice(string.ascii_uppercase))

    if use_digits:
        characters += string.digits
        password.append(secrets.choice(string.digits))

    if use_symbols:
        characters += string.punctuation
        password.append(secrets.choice(string.punctuation))

    if not characters:
        raise ValueError("At least one character set must be selected.")

    if length < len(password):
        raise ValueError("Length too short for selected character types.")

    password += [secrets.choice(characters) for _ in range(length - len(password))]
    secrets.SystemRandom().shuffle(password)

    return ''.join(password)


if __name__ == "__main__":
    print(generate_password(16))