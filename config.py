import os
from game_logic.Game import rules
from game_logic.Game.constants import ATTACKER, DEFENDER, KING, EMPTY, BOARD_SIZE as LOGIC_BOARD_SIZE

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
    INITIAL_ACTOR_CELLS = (
        ({KING_CELL} if KING_CELL else set())
        | set(DEFENDER_POSITIONS)
        | set(ATTACKERS_POSITIONS)
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


def get_game_board():
    board = [[EMPTY for _ in range(LOGIC_BOARD_SIZE)] for _ in range(LOGIC_BOARD_SIZE)]
    for i, j in ATTACKERS_POSITIONS:
        board[i][j] = ATTACKER
    for i, j in DEFENDER_POSITIONS:
        board[i][j] = DEFENDER
    if KING_CELL:
        board[KING_CELL[0]][KING_CELL[1]] = KING
    return board


class GameStateProxy:
    def __init__(self, board):
        self.board = board


def process_game_step(last_move):
    """
    last_move: (start_i, start_j, end_i, end_j)
    Returns: (winner, captured_cells)
    """
    board = get_game_board()
    state = GameStateProxy(board)

    rules.apply_captures(state, last_move)

    # Sync back the board state
    captured_cells = []

    # Check for removals
    all_current_cells = (
        set(ATTACKERS_POSITIONS.keys())
        | set(DEFENDER_POSITIONS.keys())
        | ({KING_CELL} if KING_CELL else set())
    )

    for r in range(LOGIC_BOARD_SIZE):
        for c in range(LOGIC_BOARD_SIZE):
            if (r, c) in all_current_cells and board[r][c] == EMPTY:
                # This piece was captured
                captured_cells.append((r, c))
                if (r, c) == KING_CELL:
                    global KING_CELL, KING_POSITION
                    KING_CELL = None
                    KING_POSITION = None
                elif (r, c) in ATTACKERS_POSITIONS:
                    ATTACKERS_POSITIONS.pop((r, c))
                elif (r, c) in DEFENDER_POSITIONS:
                    DEFENDER_POSITIONS.pop((r, c))

    rebuild_occupied_cells()

    winner = rules.check_winner(state)
    return winner, captured_cells


rebuild_occupied_cells()
