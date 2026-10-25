
import random
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
WORDS_FILE = BASE_DIR / "words.txt"
SCORES_FILE = BASE_DIR / "leaderboard.json"

DEFAULT_WORDS = [
    "python", "computer", "programming", "hangman",
    "keyboard", "science", "network", "software",
    "database", "internet", "developer", "education",
    "technology", "application", "student", "machine",
    "algorithm", "security", "variable", "function"
]

MAX_ATTEMPTS = 6

HANGMAN_STAGES = [
    """
     +---+
     |   |
         |
         |
         |
    ========
    """,
    """
     +---+
     |   |
     O   |
         |
         |
    ========
    """,
    """
     +---+
     |   |
     O   |
     |   |
         |
    ========
    """,
    """
     +---+
     |   |
     O   |
    /|   |
         |
    ========
    """,
    """
     +---+
     |   |
     O   |
    /|\\  |
         |
    ========
    """,
    """
     +---+
     |   |
     O   |
    /|\\  |
    /    |
    ========
    """,
    """
     +---+
     |   |
     O   |
    /|\\  |
    / \\  |
    ========
    """
]


def load_words():
    """Load the dictionary, with a built-in fallback."""
    if WORDS_FILE.exists():
        try:
            with WORDS_FILE.open(
                "r", encoding="utf-8-sig"
            ) as file:
                words = [
                    line.strip().lower()
                    for line in file
                    if line.strip().isascii()
                    and line.strip().isalpha()
                    and len(line.strip()) >= 4
                ]

            if words:
                print("English word list loaded.")
                return words

        except OSError:
            print("Could not read words.txt; using default words.")

    print("Using built-in word list.")
    return DEFAULT_WORDS.copy()


def display_word(word, guessed):
    return " ".join(
        letter.upper() if letter in guessed else "_"
        for letter in word
    )


def load_scores():
    """Read saved leaderboard data."""
    if not SCORES_FILE.exists():
        return []

    try:
        with SCORES_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (OSError, json.JSONDecodeError):
        print("Leaderboard could not be read. Starting a new one.")
        return []


def save_scores(scores):
    """Save leaderboard data to JSON."""
    try:
        with SCORES_FILE.open("w", encoding="utf-8") as file:
            json.dump(scores, file, indent=4)
    except OSError as error:
        print(f"Could not save leaderboard: {error}")


def show_leaderboard():
    scores = load_scores()

    print("\n========== LEADERBOARD ==========")

    if not scores:
        print("No scores recorded yet.")
        return

    # Show the ten highest-scoring players.
    scores.sort(key=lambda item: item.get("score", 0), reverse=True)

    for rank, entry in enumerate(scores[:10], start=1):
        print(
            f"{rank}. {entry.get('name', 'Player')} - "
            f"{entry.get('score', 0)} points "
            f"({entry.get('wins', 0)} wins)"
        )


def play_game(words, player_name, max_attempts=MAX_ATTEMPTS):
    word = random.choice(words)
    guessed = set()
    wrong = set()

    print(f"\nGuess the hidden word! You have {max_attempts} wrong guesses.")

    while len(wrong) < max_attempts:
        stage_index = min(len(wrong), len(HANGMAN_STAGES) - 1)
        print(HANGMAN_STAGES[stage_index])

        print("Word:", display_word(word, guessed))
        print("Correct letters:", ", ".join(sorted(guessed)) or "None")
        print("Wrong letters:", ", ".join(sorted(wrong)) or "None")
        print("Attempts left:", max_attempts - len(wrong))

        guess = input("Enter a letter (A-Z): ").strip().lower()

        if len(guess) != 1 or guess not in "abcdefghijklmnopqrstuvwxyz":
            print("Please enter exactly one English letter.\n")
            continue

        if guess in guessed or guess in wrong:
            print("You already guessed that letter. No penalty!\n")
            continue

        if guess in word:
            guessed.add(guess)
            print("Correct!\n")
        else:
            wrong.add(guess)
            print(f"Incorrect! '{guess.upper()}' is not in the word.\n")

        if all(letter in guessed for letter in word):
            score = 100 + (max_attempts - len(wrong)) * 20

            print("\n" + "=" * 35)
            print("       CONGRATULATIONS! YOU WIN!")
            print("=" * 35)
            print("Word:", word.upper())
            print("Points earned:", score)

            scores = load_scores()
            player = next(
                (item for item in scores
                 if item.get("name", "").casefold()
                 == player_name.casefold()),
                None
            )

            if player is None:
                player = {
                    "name": player_name,
                    "score": 0,
                    "wins": 0
                }
                scores.append(player)

            player["score"] = player.get("score", 0) + score
            player["wins"] = player.get("wins", 0) + 1
            save_scores(scores)
            return

    print(HANGMAN_STAGES[-1])
    print("\nGAME OVER! YOU LOSE!")
    print("The correct word was:", word.upper())

    scores = load_scores()
    player = next(
        (item for item in scores
         if item.get("name", "").casefold()
         == player_name.casefold()),
        None
    )

    if player is None:
        scores.append({
            "name": player_name,
            "score": 0,
            "wins": 0
        })
        save_scores(scores)


def main():
    print("=" * 35)
    print("       HANGMAN WORD GAME")
    print("=" * 35)

    player_name = input("Enter your player name: ").strip()
    if not player_name:
        player_name = "Player"

    words = load_words()

    while True:
        print("\n========== MAIN MENU ==========")
        print("1. Play game")
        print("2. View leaderboard")
        print("3. Exit")

        choice = input("Select an option (1/2/3): ").strip()

        if choice == "1":
            play_game(words, player_name)
        elif choice == "2":
            show_leaderboard()
        elif choice == "3":
            print("\nThanks for playing Hangman!")
            break
        else:
            print("Invalid option. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()
