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


def find_king(board):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == KING:
                return (r, c)
    return None


def check_winner(state):
    board = state.board
    king_pos = find_king(board)

    # King removed -> attackers win
    if king_pos is None:
        return "attacker"

    kr, kc = king_pos

    # King reaches a corner -> defenders win
    if (kr, kc) in CORNERS:
        return "defender"

    # Simple king capture check: surrounded by attackers on all 4 sides
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    blocked = 0

    for dr, dc in directions:
        nr, nc = kr + dr, kc + dc

        if not in_bounds(nr, nc):
            blocked += 1
        elif board[nr][nc] == ATTACKER:
            blocked += 1

    if blocked == 4:
        return "attacker"

    return None


def is_friendly_piece(piece, mover_piece):
    """
    King is NOT allowed to assist in capturing opponents.
    So only A can capture A, and D can capture A.
    """
    if mover_piece == ATTACKER:
        return piece == ATTACKER
    if mover_piece == DEFENDER:
        return piece == DEFENDER
    return False


def is_enemy_piece(piece, mover_piece):
    """
    What can the moving piece capture?
    Attacker can capture D and K.
    Defender can capture A.
    King cannot capture anyone.
    """
    if mover_piece == ATTACKER:
        return piece in (DEFENDER, KING)
    if mover_piece == DEFENDER:
        return piece == ATTACKER
    return False


def capture_if_flanked(state, mover_piece, enemy_r, enemy_c, dr, dc):
    board = state.board

    if not in_bounds(enemy_r, enemy_c):
        return

    enemy_piece = board[enemy_r][enemy_c]
    if enemy_piece == EMPTY:
        return

    if not is_enemy_piece(enemy_piece, mover_piece):
        return

    br, bc = enemy_r + dr, enemy_c + dc
    if not in_bounds(br, bc):
        return

    behind_piece = board[br][bc]

    # Capture is valid if the far side is:
    # - a friendly piece (but king does NOT count as friendly for capturing)
    # - the throne
    # - a corner
    if is_special_square(br, bc) or is_friendly_piece(behind_piece, mover_piece):
        board[enemy_r][enemy_c] = EMPTY


def apply_captures(state, last_move):
    fr, fc, tr, tc = last_move
    board = state.board
    mover_piece = board[tr][tc]

    # King does not capture opponents
    if mover_piece == KING:
        return state

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dr, dc in directions:
        enemy_r = tr + dr
        enemy_c = tc + dc
        capture_if_flanked(state, mover_piece, enemy_r, enemy_c, dr, dc)

    return state