from .constants import (
    BOARD_SIZE,
    EMPTY,
    ATTACKER,
    DEFENDER,
    KING,
    THRONE,
    CORNERS,
    in_bounds,
    is_enemy,
    is_friendly_piece,
)


def find_king(board):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == KING:
                return (r, c)
    return None


def is_capture_square(board, r, c, mover_piece):
    """Return True when a square can support a capture for mover_piece."""
    if not in_bounds(r, c):
        return False

    piece = board[r][c]
    if is_friendly_piece(piece, mover_piece):
        return True

    return piece == EMPTY and ((r, c) == THRONE or (r, c) in CORNERS)


def is_on_edge(r, c):
    return r == 0 or r == BOARD_SIZE - 1 or c == 0 or c == BOARD_SIZE - 1


def is_next_to_corner(r, c):
    for cr, cc in CORNERS:
        if abs(r - cr) + abs(c - cc) == 1:
            return True
    return False


def is_next_to_throne(r, c):
    tr, tc = THRONE
    return abs(r - tr) + abs(c - tc) == 1


def get_required_king_attackers(kr, kc):
    if is_next_to_corner(kr, kc):
        return 2
    if is_next_to_throne(kr, kc):
        return 3
    if is_on_edge(kr, kc):
        return 3
    return 4


def is_king_captured(board):
    king_pos = find_king(board)
    if king_pos is None:
        return True

    kr, kc = king_pos
    if (kr, kc) in CORNERS:
        return False

    attackers = 0
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = kr + dr, kc + dc
        if in_bounds(nr, nc) and board[nr][nc] == ATTACKER:
            attackers += 1

    return attackers >= get_required_king_attackers(kr, kc)


def check_winner(state):
    board = state.board
    king_pos = find_king(board)

    if king_pos is None:
        return "attacker"

    if king_pos in CORNERS:
        return "defender"

    if is_king_captured(board):
        return "attacker"

    return None


def capture_if_flanked(state, mover_piece, enemy_r, enemy_c, dr, dc):
    board = state.board

    if not in_bounds(enemy_r, enemy_c):
        return

    enemy_piece = board[enemy_r][enemy_c]
    if enemy_piece == EMPTY or enemy_piece == KING:
        return

    if not is_enemy(enemy_piece, mover_piece):
        return

    br, bc = enemy_r + dr, enemy_c + dc
    if is_capture_square(board, br, bc, mover_piece):
        board[enemy_r][enemy_c] = EMPTY


def capture_sandwiched_pieces(state):
    board = state.board

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = board[r][c]

            if piece == EMPTY or piece == KING:
                continue

            captor_piece = DEFENDER if piece == ATTACKER else ATTACKER

            if (
                is_capture_square(board, r, c - 1, captor_piece)
                and is_capture_square(board, r, c + 1, captor_piece)
            ):
                board[r][c] = EMPTY
                continue

            if (
                is_capture_square(board, r - 1, c, captor_piece)
                and is_capture_square(board, r + 1, c, captor_piece)
            ):
                board[r][c] = EMPTY
                continue


def apply_captures(state, last_move):
    _, _, tr, tc = last_move
    mover_piece = state.board[tr][tc]

    if mover_piece == KING:
        capture_sandwiched_pieces(state)
        return state

    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        enemy_r = tr + dr
        enemy_c = tc + dc
        capture_if_flanked(state, mover_piece, enemy_r, enemy_c, dr, dc)

    capture_sandwiched_pieces(state)

    return state
