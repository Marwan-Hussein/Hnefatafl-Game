import itertools
import os

CELL_SIZE = 84
internal_offset = 175
BOARD_CELLS = 9


#   ========    HELPERS     ==========
def cell(i, j):
    return (i * CELL_SIZE + 2 + internal_offset, j * CELL_SIZE + internal_offset - 20)


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
    for i in range(2, 7):  # middle three columns
        attackers[(i, 0)] = cell(i, 0)
        attackers[(i, 8)] = cell(i, 8)
        if i == 4:
            attackers[(i, 1)] = cell(i, 1)
            attackers[(i, 7)] = cell(i, 7)

    # Left and right columns (near edges)
    for j in range(2, 7):  # middle three rows
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
    defenders[(3, 3)] = cell(3, 3)
    defenders[(5, 3)] = cell(5, 3)
    defenders[(3, 5)] = cell(3, 5)
    defenders[(5, 5)] = cell(5, 5)
    return defenders


#   ========    GLOBAL VARS     ==========
BOARD_SIZE = 1024
ACTOR_SIZE = 75
AVAILABLE_BOARD_POSITIONS, KING_POSITION = positions()
KING_CELL = (4, 4)
ATTACKERS_POSITIONS = attacker_positions()
DEFENDER_POSITIONS = defender_positions()
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
CORNERS = {
    (0, 0): cell(0, 0),
    (0, 8): cell(0, 8),
    (8, 0): cell(8, 0),
    (8, 8): cell(8, 8),
}

# only for actors -> consider corners in validations or winning
INITIAL_ACTOR_CELLS = set()
OCCUPIED_CELLS = []


def rebuild_occupied_cells():
    global INITIAL_ACTOR_CELLS, OCCUPIED_CELLS
    INITIAL_ACTOR_CELLS = {KING_CELL} | set(DEFENDER_POSITIONS) | set(
        ATTACKERS_POSITIONS
    )
    OCCUPIED_CELLS = [
        [0 if (i, j) in INITIAL_ACTOR_CELLS else 1 for j in range(BOARD_CELLS)]
        for i in range(BOARD_CELLS)
    ]


def update_actor_position(actor_type, old_cell, new_cell):
    global KING_CELL, KING_POSITION

    if actor_type == "king":
        KING_CELL = new_cell
        KING_POSITION = cell(*new_cell)
    elif actor_type == "defender":
        DEFENDER_POSITIONS.pop(old_cell, None)
        DEFENDER_POSITIONS[new_cell] = cell(*new_cell)
    elif actor_type == "attacker":
        ATTACKERS_POSITIONS.pop(old_cell, None)
        ATTACKERS_POSITIONS[new_cell] = cell(*new_cell)

    rebuild_occupied_cells()


rebuild_occupied_cells()
