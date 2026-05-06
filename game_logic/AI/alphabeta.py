try:
    from ..Game.moves import get_all_moves, apply_move
    from ..Game.rules import apply_captures, check_winner
    from .evaluation import evaluate, INF
    from .difficulty import get_depth
except ImportError:
    from Game.moves import get_all_moves, apply_move
    from Game.rules import apply_captures, check_winner
    from AI.evaluation import evaluate, INF
    from AI.difficulty import get_depth


# ── helpers ───────────────────────────────────────────────────────────────────

def _opponent(player):
    return "defender" if player == "attacker" else "attacker"


def _apply_and_capture(state, move):
    new_state = state.copy()
    apply_move(new_state, move)
    apply_captures(new_state, move)
    return new_state


def _order_moves(state, moves, player):
    def quick_score(move):
        s = _apply_and_capture(state, move)
        return evaluate(s, player)

    return sorted(moves, key=quick_score, reverse=True)


# ── alpha-beta ────────────────────────────────────────────────────────────────

def alphabeta(state, depth, alpha, beta, maximizing_player, ai_player):
    winner = check_winner(state)
    if winner is not None:
        return INF if winner == ai_player else -INF

    if depth == 0:
        return evaluate(state, ai_player)

    current_player = ai_player if maximizing_player else _opponent(ai_player)
    moves = get_all_moves(state, current_player)

    if not moves:
        return -INF if maximizing_player else INF

    
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
                break          
        return value

    else:
        value = INF
        for move in moves:
            child = _apply_and_capture(state, move)
            child.turn = _opponent(current_player)
            value = min(value, alphabeta(child, depth - 1, alpha, beta, True, ai_player))
            beta = min(beta, value)
            if beta <= alpha:
                break         
        return value


# ── public interface ──────────────────────────────────────────────────────────

def get_best_move(state, player, level="medium"):
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
            False,      
            player
        )

        if value > best_value:
            best_value = value
            best_move  = move

    return best_move