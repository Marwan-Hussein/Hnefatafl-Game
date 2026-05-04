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

"""
ai/alphabeta.py

Alpha-beta pruning minimax for Hnefatafl.
Uses:
  - Game.moves    : get_all_moves, apply_move
  - Game.rules    : apply_captures, check_winner
  - AI.evaluation : evaluate
  - AI.difficulty : get_depth
"""

from Game.moves    import get_all_moves, apply_move
from Game.rules    import apply_captures, check_winner
from AI.evaluation import evaluate, INF
from AI.difficulty import get_depth


# ── helpers ───────────────────────────────────────────────────────────────────

def _opponent(player):
    return "defender" if player == "attacker" else "attacker"


def _apply_and_capture(state, move):
    """
    Return a NEW state after applying move + captures.
    Does NOT modify the original state.
    """
    new_state = state.copy()
    apply_move(new_state, move)
    apply_captures(new_state, move)
    return new_state


def _order_moves(state, moves, player):
    """
    Shallow move ordering: score each move so we search
    promising branches first → better pruning.
    """
    def quick_score(move):
        s = _apply_and_capture(state, move)
        return evaluate(s, player)

    return sorted(moves, key=quick_score, reverse=True)


# ── alpha-beta ────────────────────────────────────────────────────────────────

def alphabeta(state, depth, alpha, beta, maximizing_player, ai_player):
    """
    Standard alpha-beta minimax.

    Parameters
    ----------
    state             : current GameState
    depth             : plies remaining
    alpha, beta       : pruning bounds
    maximizing_player : True  → it's ai_player's turn
                        False → it's opponent's turn
    ai_player         : the side the AI is playing ("attacker" / "defender")

    Returns
    -------
    float : heuristic value of the state
    """
    # ── terminal / leaf ───────────────────────────────────────────────────────
    winner = check_winner(state)
    if winner is not None:
        return INF if winner == ai_player else -INF

    if depth == 0:
        return evaluate(state, ai_player)

    current_player = ai_player if maximizing_player else _opponent(ai_player)
    moves = get_all_moves(state, current_player)

    if not moves:
        return -INF if maximizing_player else INF

    # move ordering only at higher depths to keep overhead reasonable
    if depth >= 4:
        moves = _order_moves(state, moves, current_player)

    if maximizing_player:
        value = -INF
        for move in moves:
            child = _apply_and_capture(state, move)
            child.turn = _opponent(current_player)
            value = max(value, alphabeta(child, depth - 1, alpha, beta, False, ai_player))
            alpha = max(alpha, value)
            if alpha >= beta:
                break          # β-cutoff
        return value

    else:
        value = INF
        for move in moves:
            child = _apply_and_capture(state, move)
            child.turn = _opponent(current_player)
            value = min(value, alphabeta(child, depth - 1, alpha, beta, True, ai_player))
            beta = min(beta, value)
            if beta <= alpha:
                break          # α-cutoff
        return value


# ── public interface ──────────────────────────────────────────────────────────

def get_best_move(state, player, level="medium"):
    """
    Choose the best move for `player` at the given difficulty level.

    Parameters
    ----------
    state  : current GameState
    player : "attacker" or "defender"
    level  : "easy" | "medium" | "hard"

    Returns
    -------
    tuple (fr, fc, tr, tc) or None if no moves exist
    """
    depth = get_depth(level)
    moves = get_all_moves(state, player)

    if not moves:
        return None

    best_move  = None
    best_value = -INF

    for move in moves:
        child = _apply_and_capture(state, move)
        child.turn = _opponent(player)

        value = alphabeta(
            child,
            depth - 1,
            -INF,
            INF,
            False,      # opponent moves next → minimizing
            player
        )

        if value > best_value:
            best_value = value
            best_move  = move

    return best_move