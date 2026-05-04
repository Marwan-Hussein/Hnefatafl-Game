# ai/evaluation.py
#utility function here
# You implement:
# - board scoring function
# - evaluates a game state from a given player's perspective
# - heuristics:
#     * material advantage (attackers vs defenders)
#     * king safety (distance to escape corners)
#     * positional advantage
#
# Goal:
# - assign a numeric score to any board state
# - used by alpha-beta pruning to choose best move
# ai/evaluation.py

from Game.constants import (
    BOARD_SIZE, ATTACKER, DEFENDER, KING, CORNERS
)
from Game.rules import check_winner

MATERIAL_WEIGHT = 2
KING_DISTANCE_WEIGHT = 6
MOBILITY_WEIGHT = 1.5
WIN_WEIGHT = 10000


def manhattan_distance(r1, c1, r2, c2):
    return abs(r1 - r2) + abs(c1 - c2)


def find_king(board):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == KING:
                return (r, c)
    return None


def material_score(board):
    attackers = 0
    defenders = 0

    for row in board:
        for cell in row:
            if cell == ATTACKER:
                attackers += 1
            elif cell == DEFENDER:
                defenders += 1

    return defenders - attackers


def king_distance_score(board):
    king_pos = find_king(board)

    if not king_pos:
        return -WIN_WEIGHT

    kr, kc = king_pos

    min_dist = min(
        manhattan_distance(kr, kc, cr, cc)
        for (cr, cc) in CORNERS
    )

    return -min_dist


def mobility_score(state, player):
    from Game.moves import get_all_moves
    return len(get_all_moves(state, player))


def evaluate(state, player):
    board = state.board

    #  Check win/lose first
    winner = check_winner(state)
    if winner == "defender":
        return WIN_WEIGHT if player == "defender" else -WIN_WEIGHT
    elif winner == "attacker":
        return WIN_WEIGHT if player == "attacker" else -WIN_WEIGHT

    # Material
    material = material_score(board) * MATERIAL_WEIGHT

    # King safety
    king_dist = king_distance_score(board) * KING_DISTANCE_WEIGHT

    # Mobility
    if player == "attacker":
        mobility = mobility_score(state, "attacker") - mobility_score(state, "defender")
    else:
        mobility = mobility_score(state, "defender") - mobility_score(state, "attacker")

    mobility *= MOBILITY_WEIGHT

    score = material + king_dist + mobility

    #  flip perspective
    if player == "attacker":
        score = -score

    return score