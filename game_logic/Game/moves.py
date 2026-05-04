from .constants import (
    BOARD_SIZE, EMPTY, ATTACKER, DEFENDER, KING,
    THRONE, CORNERS, in_bounds, is_special_square, is_enemy
)


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

            # Allow moves into sandwich positions - piece will be captured after moving
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