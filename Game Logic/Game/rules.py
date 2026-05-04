from .constants import (
    BOARD_SIZE, EMPTY, ATTACKER, DEFENDER, KING,
    CORNERS, in_bounds, is_special_square, is_enemy, is_friendly_piece
)


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

    # King capture check: surrounded by attackers
    # Count how many sides are blocked (by attackers or board edges)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    blocked_sides = 0

    for dr, dc in directions:
        nr, nc = kr + dr, kc + dc

        if not in_bounds(nr, nc):
            blocked_sides += 1  # Board edge blocks movement
        elif board[nr][nc] == ATTACKER:
            blocked_sides += 1  # Attacker blocks movement

    # King is captured if all sides are blocked
    if blocked_sides == 4:
        return "attacker"

    return None


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

    behind_piece = board[br][bc]

    # Capture is valid if the far side is:
    # - a friendly piece (but king does NOT count as friendly for capturing)
    # - an empty throne
    # - an empty corner
    if (is_special_square(br, bc) and board[br][bc] == EMPTY) or is_friendly_piece(behind_piece, mover_piece):
        board[enemy_r][enemy_c] = EMPTY


def capture_sandwiched_pieces(state):
    """
    Custodial Capture: Remove pieces that are sandwiched between two opposing pieces.
    Check all pieces on the board after each move.
    """
    board = state.board

    # Check each position on the board
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = board[r][c]
            if piece == EMPTY or piece == KING:  # King cannot be captured by sandwich
                continue

            # Check horizontal sandwich (left and right)
            if in_bounds(r, c - 1) and in_bounds(r, c + 1):
                left = board[r][c - 1]
                right = board[r][c + 1]
                if left != EMPTY and right != EMPTY:
                    # Check if both sides are enemies of this piece
                    if is_enemy(left, piece) and is_enemy(right, piece):
                        board[r][c] = EMPTY
                        continue

            # Check vertical sandwich (up and down)
            if in_bounds(r - 1, c) and in_bounds(r + 1, c):
                up = board[r - 1][c]
                down = board[r + 1][c]
                if up != EMPTY and down != EMPTY:
                    # Check if both sides are enemies of this piece
                    if is_enemy(up, piece) and is_enemy(down, piece):
                        board[r][c] = EMPTY
                        continue


def apply_captures(state, last_move):
    fr, fc, tr, tc = last_move
    board = state.board
    mover_piece = board[tr][tc]

    # King does not capture opponents
    if mover_piece == KING:
        # Still apply sandwich captures for other pieces
        capture_sandwiched_pieces(state)
        return state

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # Apply flanking captures (between piece and throne/corner)
    for dr, dc in directions:
        enemy_r = tr + dr
        enemy_c = tc + dc
        capture_if_flanked(state, mover_piece, enemy_r, enemy_c, dr, dc)

    # Apply custodial captures (sandwich between two enemy pieces)
    capture_sandwiched_pieces(state)

    return state