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


def is_sandwich(board, r, c, mover_piece):
    """
    Return True only if the landing square is between two ENEMY pieces
    horizontally or vertically.
    This will not block friendly formations like D - D for the king.
    """
    # horizontal check
    if in_bounds(r, c - 1) and in_bounds(r, c + 1):
        left = board[r][c - 1]
        right = board[r][c + 1]

        if left != EMPTY and right != EMPTY:
            if is_enemy(left, mover_piece) and is_enemy(right, mover_piece):
                return True

    # vertical check
    if in_bounds(r - 1, c) and in_bounds(r + 1, c):
        up = board[r - 1][c]
        down = board[r + 1][c]

        if up != EMPTY and down != EMPTY:
            if is_enemy(up, mover_piece) and is_enemy(down, mover_piece):
                return True

    return False


def get_piece_moves(state, row, col):
    board = state.board
    piece = board[row][col]

    if piece == EMPTY:
        return []

    moves = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dr, dc in directions:
        r, c = row + dr, col + dc

        while in_bounds(r, c):
            if board[r][c] != EMPTY:
                break

            # only king can enter throne/corners
            if piece != KING and is_special_square(r, c):
                break

            # block only if the square is between two ENEMY pieces
            if is_sandwich(board, r, c, piece):
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