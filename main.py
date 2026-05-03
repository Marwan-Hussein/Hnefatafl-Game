import tkinter as tk
from PIL import Image, ImageTk
import os


def main():
    # set the main board
    root = tk.Tk()
    root.title("Hnefatafl Game")

    # used dimensions
    BOARD_SIZE = 1024
    DISPLAY_WIDTH = 1820  # approximatly = 1024 * 16/9
    DISPLAY_HEIGHT = 1024
    ACTOR_SIZE = 89
    root.geometry(f"{DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")

    # used paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, "assets", "icon.ico")
    board_path = os.path.join(current_dir, "assets", "GameBoard.png")

    # verfy file exists to avoid crashes
    if not os.path.exists(board_path):
        print(f"Error: couldn't find the path: {board_path}")
        return

    # customize icon
    root.iconbitmap(icon_path)

    # create the canvas
    canvas = tk.Canvas(
        root,
        width=DISPLAY_WIDTH,
        height=DISPLAY_HEIGHT,
        highlightthickness=0,
        bg="#F5EDDA",
    )  # to be with screen's width
    canvas.pack(fill="both", expand=True)

    # load the png file (GameBoard)
    try:
        board_img = Image.open(board_path).resize(
            (BOARD_SIZE, BOARD_SIZE), Image.LANCZOS
        )

        # Convert to be as Tkinter Image
        main_board = ImageTk.PhotoImage(board_img)

        # place the image to be centered
        canvas.create_image(
            canvas_width // 2,
            canvas_height // 2,
            image=main_board,
            anchor=tk.CENTER,
            tags="board",
        )

        # ref to the canvas
        canvas.board_image = main_board

    except Exception as e:
        print(f"Faild to load PNG: {e}")

    root.mainloop()


if __name__ == "__main__":
    main()
