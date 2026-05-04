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
from Game.rules import apply_captures, check_winner
from AI.evaluation import evaluate


def get_opponent(player):
    return "defender" if player == "attacker" else "attacker"


def minimax(state, depth, alpha, beta, maximizing, player):
    #  Check terminal state
    winner = check_winner(state)
    if depth == 0 or winner:
        return evaluate(state, player), None

    moves = get_all_moves(state, state.turn)

    if not moves:
        return evaluate(state, player), None

    best_move = None

    if maximizing:
        max_eval = -math.inf

        for move in moves:
            new_state = copy.deepcopy(state)

            apply_move(new_state, move)
            apply_captures(new_state, move)
            new_state.switch_turn()

            eval_score, _ = minimax(
                new_state,
                depth - 1,
                alpha,
                beta,
                False,
                player
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
            apply_captures(new_state, move)
            new_state.switch_turn()

            eval_score, _ = minimax(
                new_state,
                depth - 1,
                alpha,
                beta,
                True,
                player
            )

            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move

            beta = min(beta, eval_score)
            if beta <= alpha:
                break

        return min_eval, best_move


def get_best_move(state, player, level):
    from AI.difficulty import get_depth

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