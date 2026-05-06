

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
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def is_special_square(r, c):
    return (r, c) == THRONE or (r, c) in CORNERS


def is_enemy(other_piece, mover_piece):

    if mover_piece == ATTACKER:
        return other_piece in (DEFENDER, KING)
    elif mover_piece in (DEFENDER, KING):
        return other_piece == ATTACKER
    return False


def is_friendly_piece(piece, mover_piece):
  
    if mover_piece == ATTACKER:
        return piece == ATTACKER
    if mover_piece == DEFENDER:
        return piece == DEFENDER
    return False
