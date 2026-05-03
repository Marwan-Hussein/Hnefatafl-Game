from Game.state import GameState
from Game.moves import get_all_moves, apply_move
from Game.rules import check_winner, apply_captures


def get_human_move():
    move = input("Move (from_row from_col to_row to_col): ")
    fr, fc, tr, tc = map(int, move.split())
    return (fr, fc, tr, tc)


def get_ai_move(state):
    moves = get_all_moves(state, state.turn)
    if not moves:
        return None
    return moves[0]


def choose_mode():
    print("1 - Human vs Human")
    print("2 - Human vs Computer")
    return input("Choose: ")


def choose_side():
    print("Choose your side:")
    print("1 - Attacker")
    print("2 - Defender")
    choice = input("Choose: ")
    return "attacker" if choice == "1" else "defender"


def run_game():
    state = GameState()
    mode = choose_mode()

    human_side = None
    if mode == "2":
        human_side = choose_side()

    print("Attacker moves first!")
    state.print_board()

    while True:
        print(f"\nTurn: {state.turn}")

        if mode == "1":
            move = get_human_move()

        else:
            if state.turn == human_side:
                move = get_human_move()
            else:
                move = get_ai_move(state)
                print("AI Move:", move)

        if move is None:
            break

        apply_move(state, move)
        apply_captures(state, move)

        state.print_board()

        winner = check_winner(state)
        if winner:
            print("Game Over:", winner)
            break

        state.switch_turn()