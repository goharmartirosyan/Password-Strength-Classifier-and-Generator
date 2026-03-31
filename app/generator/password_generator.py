import secrets
import string

def generate_password(length=12, use_upper=True, use_lower=True, use_digits=True, use_symbols=True):
    characters = ""

    if use_lower:
        characters += string.ascii_lowercase
    if use_upper:
        characters += string.ascii_uppercase
    if use_digits:
        characters += string.digits
    if use_symbols:
        characters += string.punctuation
        

    if not characters:
        raise ValueError("At least one character set must be selected.")

    # Ensure randomness using CSPRNG
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


if __name__ == "__main__":
    print(generate_password(16))