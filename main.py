import tkinter as tk
from PIL import Image, ImageTk
import os


def main():
    # set the main board
    root = tk.Tk()
    root.title("Hnefatafl Game")

    # used dimensions
    BOARD_SIZE = 1024
    screen_w = root.winfo_screenwidth()  # approximatly = 1024 * 16/9
    screen_h = root.winfo_screenheight()
    ACTOR_SIZE = 89

    fit_size = min(screen_w, screen_h)
    scale = BOARD_SIZE / fit_size
    root.geometry(f"{screen_w}x{screen_h}")

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
        width=screen_w,
        height=screen_h,
        highlightthickness=0,
        bg="#F5EDDA",
    )  # to be with screen's width
    canvas.pack(fill="both", expand=True)

    # load the png file (GameBoard)
    try:
        board_img = Image.open(board_path).resize(
            (int(BOARD_SIZE / scale), int(BOARD_SIZE / scale)), Image.LANCZOS
        )

        # Convert to be as Tkinter Image
        main_board = ImageTk.PhotoImage(board_img)

        # place the image to be centered

        root.update_idletasks()
        titlebar_h = root.winfo_rooty() - root.winfo_y()
        canvas.create_image(
            screen_w // 2,
            screen_h // 2 - titlebar_h //2,
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
