import secrets

SUBSTITUTIONS = {
    'a': '4',
    'e': '3',
    'i': '1',
    'o': '0',
    's': '$',
    'k': 'x',  
    't': '7'
}

def transform_word(word):
    word = list(word.lower())

    num_replacements = secrets.choice([1, 2])

    indices = list(range(len(word)))
    secrets.SystemRandom().shuffle(indices)

    replaced = 0

    for i in indices:
        char = word[i]
        if char in SUBSTITUTIONS:
            word[i] = SUBSTITUTIONS[char]
            replaced += 1

        if replaced >= num_replacements:
            break

    if replaced == 0:
        insert_index = secrets.randbelow(len(word))
        word.insert(insert_index, secrets.choice("!@#$%"))
    return ''.join(word).capitalize()

def generate_personalized_password(fruit, street, number):
    symbol = secrets.choice("!@#$%")

    part1 = transform_word(fruit)
    part2 = transform_word(street.title())

    return f"{part1}{symbol}{part2}{number}"


if __name__ == "__main__":
    print(generate_personalized_password("oring", "Amiryan", 12))