from Game.state import GameState
from Game.moves import get_all_moves, apply_move
from Game.rules import check_winner, apply_captures
import random


def format_pos(row, col):
    """Convert (row, col) -> chess-style position like a7."""
    return chr(col + ord('a')) + str(row + 1)


def parse_pos(pos):
    """
    Convert position like 'a7' or 'b10' into (row, col).
    Raises ValueError if the format is invalid.
    """
    pos = pos.strip().lower()

    if len(pos) < 2:
        raise ValueError("Invalid position")

    col_char = pos[0]
    row_part = pos[1:]

    if not col_char.isalpha() or not row_part.isdigit():
        raise ValueError("Invalid position")

    col = ord(col_char) - ord('a')
    row = int(row_part) - 1

    if col < 0 or row < 0:
        raise ValueError("Invalid position")

    return row, col


def choose_mode():
    print("1 - Human vs Human")
    print("2 - Human vs Computer")
    while True:
        mode = input("Choose: ").strip()
        if mode in ("1", "2"):
            return mode
        print("Invalid choice. Enter 1 or 2.")


def choose_side():
    print("Choose your side:")
    print("1 - Attacker")
    print("2 - Defender")

    while True:
        choice = input("Choose: ").strip()
        if choice == "1":
            return "attacker"
        elif choice == "2":
            return "defender"
        print("Invalid choice. Enter 1 or 2.")


def get_piece_position(state):
    """
    Ask the user to choose a piece position.
    The piece must have at least one legal move.
    """
    all_moves = get_all_moves(state, state.turn)

    if not all_moves:
        return None

    while True:
        pos_text = input(f"\nChoose a piece for {state.turn} (e.g. g1): ").strip()

        try:
            row, col = parse_pos(pos_text)
        except ValueError:
            print("Invalid position format. Example: g1")
            continue

        piece_moves = [m for m in all_moves if m[0] == row and m[1] == col]

        if not piece_moves:
            print("No available moves for this piece. Choose another one.")
            continue

        return row, col, pos_text, piece_moves


def choose_move_from_list(pos_text, piece_moves):
    """
    Show all legal moves for the selected piece and let the user choose one.
    """
    print(f"\nAvailable moves for {pos_text}:")
    for i, move in enumerate(piece_moves, 1):
        tr, tc = move[2], move[3]
        print(f"{i}. {format_pos(tr, tc)}")

    while True:
        choice = input("Choose move number: ").strip()

        if not choice.isdigit():
            print("Please enter a valid number.")
            continue

        choice = int(choice)

        if not (1 <= choice <= len(piece_moves)):
            print("Invalid move number.")
            continue

        return piece_moves[choice - 1]


def get_human_move(state):
    """
    Human move:
    1. choose a piece
    2. show its legal moves
    3. choose one move
    """
    piece_info = get_piece_position(state)
    if piece_info is None:
        return None

    _, _, pos_text, piece_moves = piece_info
    return choose_move_from_list(pos_text, piece_moves)


def get_ai_move(state):
    """
    Simple AI: pick a random legal move.
    """
    moves = get_all_moves(state, state.turn)
    if not moves:
        return None
    return random.choice(moves)


def move_to_text(move):
    """
    Convert (fr, fc, tr, tc) into readable text.
    """
    fr, fc, tr, tc = move
    return f"{format_pos(fr, fc)} -> {format_pos(tr, tc)}"


def run_game():
    state = GameState()
    mode = choose_mode()

    human_side = None
    if mode == "2":
        human_side = choose_side()

    print("\nAttacker moves first!")
    state.print_board()

    while True:
        print(f"\nTurn: {state.turn}")

        # Check if current player has any legal moves
        legal_moves = get_all_moves(state, state.turn)
        if not legal_moves:
            # Current player has no moves, opponent wins
            opponent = "defender" if state.turn == "attacker" else "attacker"
            print(f"\nNo moves available for {state.turn}!")
            print(f"Game Over: {opponent} (opponent wins)")
            break

        # Get move
        if mode == "1":
            move = get_human_move(state)
        else:
            if state.turn == human_side:
                move = get_human_move(state)
            else:
                move = get_ai_move(state)
                if move is not None:
                    print("AI Move:", move_to_text(move))

        # No available move (should not happen after check above, but keep as safety)
        if move is None:
            print("No moves available!")
            break

        # Safety check: make sure move is legal
        if move not in legal_moves:
            print("Illegal move! Try again.")
            continue

        # Apply move
        apply_move(state, move)
        apply_captures(state, move)

        # Show board
        state.print_board()

        # Check winner
        winner = check_winner(state)
        if winner:
            print("\nGame Over:", winner)
            break

        # Next turn
        state.switch_turn()


if __name__ == "__main__":
    run_game()