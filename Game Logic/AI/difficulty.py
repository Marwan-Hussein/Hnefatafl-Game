# ai/difficulty.py

EASY = 1
MEDIUM = 3
HARD = 5


def get_depth(level):
    level = level.lower()

    if level == "easy":
        return EASY
    elif level == "medium":
        return MEDIUM
    elif level == "hard":
        return HARD
    else:
        return MEDIUM