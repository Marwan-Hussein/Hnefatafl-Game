# =========================
# HNEFATAFL - CONTROLLER
# =========================

from Game.state import GameState
from Game.moves import get_all_moves, apply_move
from Game.rules import check_winner, apply_captures


# -------------------------
# GET HUMAN MOVE (SIMPLE INPUT)
# -------------------------
def get_human_move(state):
    print("\nEnter move: from_row from_col to_row to_col")
    move = input("Move: ")

    fr, fc, tr, tc = map(int, move.split())
    return (fr, fc, tr, tc)


# -------------------------
# FIND FIRST VALID AI MOVE (TEMP SIMPLE AI)
# (later replaced by alpha-beta)
# -------------------------
def get_ai_move(state):
    moves = get_all_moves(state, state.turn)

    if len(moves) == 0:
        return None

    return moves[0]  # placeholder (will be replaced by alpha-beta)


# -------------------------
# GAME LOOP
# -------------------------
def run_game():
    state = GameState()

    print("\n=== HNEFATAFL GAME START ===")
    state.print_board()

    while True:

        print(f"\nTurn: {state.turn}")

        # -------------------------
        # GET MOVE
        # -------------------------
        if state.turn == "attacker":
            move = get_ai_move(state)
            print("AI Move:", move)
        else:
            move = get_human_move(state)

        if move is None:
            print("No moves available!")
            break

        # -------------------------
        # APPLY MOVE
        # -------------------------
        apply_move(state, move)
        apply_captures(state, move)

        # -------------------------
        # PRINT BOARD
        # -------------------------
        state.print_board()

        # -------------------------
        # CHECK WIN CONDITION
        # -------------------------
        winner = check_winner(state)

        if winner:
            print("\n=== GAME OVER ===")
            print("Winner:", winner)
            break

        # -------------------------
        # SWITCH TURN
        # -------------------------
        state.switch_turn()