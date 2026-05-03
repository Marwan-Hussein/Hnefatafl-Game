BOARD_SIZE = 9

EMPTY = "."
ATTACKER = "A"
DEFENDER = "D"
KING = "K"


def in_bounds(r, c):
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def find_king(board):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == KING:
                return (r, c)
    return None


def check_winner(state):
    board = state.board

    king_pos = find_king(board)

    if king_pos is None:
        return "attacker"

    kr, kc = king_pos

    corners = [(0, 0), (0, 8), (8, 0), (8, 8)]
    if (kr, kc) in corners:
        return "defender"

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


def check_capture(state, r, c):
    board = state.board
    piece = board[r][c]

    if piece == EMPTY:
        return

    opponent = DEFENDER if piece == ATTACKER else ATTACKER
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dr, dc in directions:
        r1, c1 = r + dr, c + dc
        r2, c2 = r + 2 * dr, c + 2 * dc

        if not (in_bounds(r1, c1) and in_bounds(r2, c2)):
            continue

        if board[r1][c1] == opponent and board[r2][c2] == piece:
            board[r1][c1] = EMPTY


def apply_captures(state, last_move):
    fr, fc, tr, tc = last_move

    check_capture(state, tr + 1, tc)
    check_capture(state, tr - 1, tc)
    check_capture(state, tr, tc + 1)
    check_capture(state, tr, tc - 1)

    return state