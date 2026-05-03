import itertools
import os

CELL_SIZE = 84


#   ========    HELPERS     ==========
def cell(i, j):
    start_poistion = 175
    return (i * CELL_SIZE + 2 + start_poistion, j * CELL_SIZE + start_poistion - 20)


def positions():
    cells = {}
    for i in range(10):
        for j in range(10):
            if (
                (i, j) == (0, 0)
                or (i, j) == (0, 8)
                or (i, j) == (8, 0)
                or (i, j) == (8, 8)
            ):
                continue  # corner positions
            cells[(i, j)] = cell(i, j)
            if (i, j) == (4, 4):
                king_pos = cell(i, j)
    return cells, king_pos


def attacker_positions():
    attackers = {}

    # Top and bottom rows (near edges)
    for i in range(3, 6):  # middle three columns
        attackers[(i, 0)] = cell(i, 0)
        attackers[(i, 8)] = cell(i, 8)
        if i == 4:
            attackers[(i, 1)] = cell(i, 1)
            attackers[(i, 7)] = cell(i, 7)

    # Left and right columns (near edges)
    for j in range(3, 6):  # middle three rows
        attackers[(0, j)] = cell(0, j)
        attackers[(8, j)] = cell(8, j)
        if j == 4:
            attackers[(1, j)] = cell(1, j)
            attackers[(7, j)] = cell(7, j)
    return attackers


def defender_positions():
    defenders = {}
    for i in range(2, 7):
        if i == 4:
            continue
        defenders[(i, 4)] = cell(i, 4)
        defenders[(4, i)] = cell(4, i)
    return defenders


#   ========    GLOBAL VARS     ==========
BOARD_SIZE = 1024
ACTOR_SIZE = 75
AVAILABLE_BOARD_POSITIONS, KING_POSITION = positions()
ATTACKERS_POSITIONS = attacker_positions()
DEFENDER_POSITIONS = defender_positions()
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
