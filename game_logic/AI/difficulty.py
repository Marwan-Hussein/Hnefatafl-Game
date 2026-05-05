# ai/difficulty.py

EASY = 1
MEDIUM = 2
HARD = 3


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
