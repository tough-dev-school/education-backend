import random
from os.path import dirname
from pathlib import Path

base_dir = Path(dirname(__file__))


def random_name() -> str:
    with open(base_dir / "adjectives.txt") as f:
        adjectives = [line.strip() for line in f if line.strip()]

    with open(base_dir / "nouns.txt") as f:
        nouns = [line.strip() for line in f if line.strip()]

    adjective = random.choice(adjectives).title()
    noun = random.choice(nouns)

    name = f"{adjective} {noun}"

    if name == "Медленный питон":  # python is fast, try one more time
        return random_name()

    return name
