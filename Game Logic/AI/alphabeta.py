# You implement:
# minimax with pruning
# uses:
# moves.py
# evaluation.py
# depth control (easy/medium/hard)
# Goal:
#
# AI can pick best move
# ai/alphabeta.py

import math
import copy

from Game.moves import get_all_moves, apply_move
from .evaluation import evaluate


def get_opponent(player):
    return "defender" if player == "attacker" else "attacker"


def minimax(state, depth, alpha, beta, maximizing, player):
    if depth == 0:
        return evaluate(state, player), None

    moves = get_all_moves(state, player)

    if not moves:
        return evaluate(state, player), None

    best_move = None

    if maximizing:
        max_eval = -math.inf

        for move in moves:
            new_state = copy.deepcopy(state)
            apply_move(new_state, move)

            eval_score, _ = minimax(
                new_state,
                depth - 1,
                alpha,
                beta,
                False,
                get_opponent(player)
            )

            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move

            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break

        return max_eval, best_move

    else:
        min_eval = math.inf

        for move in moves:
            new_state = copy.deepcopy(state)
            apply_move(new_state, move)

            eval_score, _ = minimax(
                new_state,
                depth - 1,
                alpha,
                beta,
                True,
                get_opponent(player)
            )

            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move

            beta = min(beta, eval_score)
            if beta <= alpha:
                break

        return min_eval, best_move


def get_best_move(state, player, level):
    from .difficulty import get_depth

    depth = get_depth(level)

    _, move = minimax(
        state,
        depth,
        -math.inf,
        math.inf,
        True,
        player
    )

    return move