from .constants import (
    BOARD_SIZE, EMPTY, ATTACKER, DEFENDER, KING,
    THRONE, CORNERS, in_bounds, is_special_square, is_enemy, is_friendly_piece
)


def find_king(board):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == KING:
                return (r, c)
    return None


def is_blocked(board, r, c, piece):
    """Check if a specific direction is blocked for the King."""
    if not in_bounds(r, c):
        return True
    if board[r][c] == ATTACKER:
        return True
    if (r, c) in CORNERS:
        return True
    if (r, c) == THRONE:
        return True
    return False


def check_winner(state):
    board = state.board
    king_pos = find_king(board)

    if king_pos is None:
        return "attacker"  # King captured (safety rule)

    kr, kc = king_pos

    # 🏆 Defender win
    if (kr, kc) in CORNERS:
        return "defender"

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    attackers = 0
    natural_blockers = 0

    for dr, dc in directions:
        nr, nc = kr + dr, kc + dc

        if not in_bounds(nr, nc):
            natural_blockers += 1  # Board edge counts as natural blocker
        elif board[nr][nc] == ATTACKER:
            attackers += 1
        elif (nr, nc) in CORNERS:
            natural_blockers += 1  # Corner counts as natural blocker
        elif (nr, nc) == THRONE and board[nr][nc] == EMPTY:
            natural_blockers += 1  # Empty throne counts as natural blocker

    # 🧠 Required attackers based on king position
    # Total blocker capacity = 4, natural blockers reduce attacker requirement
    if is_next_to_corner(kr, kc):
        required_attackers = 2  # Need 2 attackers (2 natural blockers: edge+corner)
    elif is_next_to_throne(kr, kc):
        required_attackers = 3  # Need 3 attackers (1 natural blocker: throne)
    elif is_on_edge(kr, kc):
        required_attackers = 3  # Need 3 attackers (1 natural blocker: edge)
    else:
        required_attackers = 4  # Need 4 attackers (no natural blockers)

    # King is captured only if there are enough attackers
    if attackers >= required_attackers:
        return "attacker"

    return None


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


def capture_if_flanked(state, mover_piece, enemy_r, enemy_c, dr, dc):
    board = state.board

    if not in_bounds(enemy_r, enemy_c):
        return

    enemy_piece = board[enemy_r][enemy_c]
    if enemy_piece == EMPTY:
        return

    if not is_enemy(enemy_piece, mover_piece):
        return

    br, bc = enemy_r + dr, enemy_c + dc
    if not in_bounds(br, bc):
        return

    behind = board[br][bc]

    if behind == ATTACKER or (behind == THRONE and board[br][bc] == EMPTY) or (behind in CORNERS and board[br][bc] == EMPTY):
        board[enemy_r][enemy_c] = EMPTY


def capture_sandwiched_pieces(state):
    board = state.board

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = board[r][c]

            if piece == EMPTY or piece == KING:
                continue

            # Horizontal
            if in_bounds(r, c - 1) and in_bounds(r, c + 1):
                left = board[r][c - 1]
                right = board[r][c + 1]

                if is_enemy(left, piece) and is_enemy(right, piece):
                    board[r][c] = EMPTY
                    continue

            # Vertical
            if in_bounds(r - 1, c) and in_bounds(r + 1, c):
                up = board[r - 1][c]
                down = board[r + 1][c]

                if is_enemy(up, piece) and is_enemy(down, piece):
                    board[r][c] = EMPTY
                    continue


def apply_captures(state, last_move):
    fr, fc, tr, tc = last_move
    board = state.board
    mover_piece = board[tr][tc]

    if mover_piece == KING:
        capture_sandwiched_pieces(state)
        return state

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dr, dc in directions:
        enemy_r = tr + dr
        enemy_c = tc + dc

        capture_if_flanked(state, mover_piece, enemy_r, enemy_c, dr, dc)

    capture_sandwiched_pieces(state)

    return state