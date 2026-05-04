"""
Centralized constants and utility functions for Hnefatafl game.
"""

BOARD_SIZE = 9

EMPTY = " "
ATTACKER = "A"
DEFENDER = "D"
KING = "K"

THRONE = (BOARD_SIZE // 2, BOARD_SIZE // 2)
CORNERS = {
    (0, 0),
    (0, BOARD_SIZE - 1),
    (BOARD_SIZE - 1, 0),
    (BOARD_SIZE - 1, BOARD_SIZE - 1),
}


def in_bounds(r, c):
    """Check if position (r, c) is within the board."""
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def is_special_square(r, c):
    """Check if position is a throne or corner."""
    return (r, c) == THRONE or (r, c) in CORNERS


def is_enemy(other_piece, mover_piece):
    """
    Decide whether other_piece is an enemy of mover_piece.

    Attacker -> enemies are Defender and King
    Defender -> enemies are Attacker
    King     -> enemies are Attacker
    """
    if mover_piece == ATTACKER:
        return other_piece in (DEFENDER, KING)
    elif mover_piece in (DEFENDER, KING):
        return other_piece == ATTACKER
    return False


def is_friendly_piece(piece, mover_piece):
    """
    Identify if a piece is friendly to mover_piece.
    King is NOT allowed to assist in capturing opponents.
    So only A can capture A, and D can capture D.
    """
    if mover_piece == ATTACKER:
        return piece == ATTACKER
    if mover_piece == DEFENDER:
        return piece == DEFENDER
    return False
