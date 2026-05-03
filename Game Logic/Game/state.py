BOARD_SIZE = 9

EMPTY = "."
ATTACKER = "A"
DEFENDER = "D"
KING = "K"


class GameState:
    def __init__(self):
        self.board = self.create_board()
        self.turn = "attacker"

    def create_board(self):
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        board[4][4] = KING

        defenders = [
            (4, 3), (4, 5),
            (3, 4), (5, 4),
            (3, 3), (3, 5),
            (5, 3), (5, 5),
            (2, 4), (6, 4),
            (4, 2), (4, 6)
        ]

        for r, c in defenders:
            board[r][c] = DEFENDER

        attackers = [
            (0, 3), (0, 4), (0, 5), (1, 4),
            (8, 3), (8, 4), (8, 5), (7, 4),
            (3, 0), (4, 0), (5, 0), (4, 1),
            (3, 8), (4, 8), (5, 8), (4, 7),
            (1, 3), (1, 5), (7, 3), (7, 5),
            (3, 1), (5, 1), (3, 7), (5, 7)
        ]

        for r, c in attackers:
            board[r][c] = ATTACKER

        return board

    def print_board(self):
        size = BOARD_SIZE
        print("    " + "   ".join(chr(ord('A') + i) for i in range(size)))
        print("   +" + "---+" * size)
        for i in range(size):
            row_num = size - i
            row_str = f"{row_num:2} |"
            for j in range(size):
                row_str += f" {self.board[i][j]} |"
            print(row_str)

            if i < size - 1:
                print("   +" + "---+" * size)

        print("   +" + "---+" * size)

    def get_piece(self, row, col):
        return self.board[row][col]

    def set_piece(self, row, col, value):
        self.board[row][col] = value

    def switch_turn(self):
        if self.turn == "attacker":
            self.turn = "defender"
        else:
            self.turn = "attacker"

    def copy(self):
        new_state = GameState()
        new_state.board = [row[:] for row in self.board]
        new_state.turn = self.turn
        return new_state