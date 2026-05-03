BOARD_SIZE = 9

EMPTY = "."
ATTACKER = "A"
DEFENDER = "D"
KING = "K"


def in_bounds(r, c):
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def get_piece_moves(state, row, col):
    board = state.board
    piece = board[row][col]

    if piece == EMPTY:
        return []

    moves = []

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    for dr, dc in directions:
        r, c = row + dr, col + dc

        while in_bounds(r, c):

            if board[r][c] != EMPTY:
                break

            moves.append((row, col, r, c))

            r += dr
            c += dc

    return moves


def get_all_moves(state, player):
    board = state.board
    all_moves = []

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):

            piece = board[r][c]

            if player == "attacker" and piece == ATTACKER:
                all_moves.extend(get_piece_moves(state, r, c))

            elif player == "defender" and piece in (DEFENDER, KING):
                all_moves.extend(get_piece_moves(state, r, c))

    return all_moves


def apply_move(state, move):
    fr, fc, tr, tc = move
    board = state.board

    piece = board[fr][fc]

    board[tr][tc] = piece
    board[fr][fc] = EMPTY

    return state