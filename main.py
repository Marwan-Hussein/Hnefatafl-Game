import tkinter as tk
import tksvg
import os

def main():
    # set the main board
    root = tk.Tk()
    root.title("Hnefatafl Game")

    BOARD_SIZE = 969
    ACTOR_SIZE = 88

    script_dir = os.path.dirname(os.path.abspath(__file__))
    board_path = os.path.join(script_dir, "assets", "GameBoard.svg")
    
    # customize icon
    icon_path = os.path.join(script_dir, "assets", "icon.ico")
    root.iconbitmap(icon_path)
    
    # verfy file exists to avoid crashes
    if not os.path.exists(board_path):
        print(f"Error: couldn't find the path: {board_path}")
        return
    

    # create the canvas
    canvas = tk.Canvas(root, width=BOARD_SIZE, height=BOARD_SIZE, highlightthickness=0, bg="#F5EDDA")
    canvas.pack()

    #load the svg file (board)
    try:
        original_height = tksvg.SvgImage(file=board_path).height()
        
        main_board = tksvg.SvgImage(file=board_path, scale= BOARD_SIZE / original_height)
        
        # Place the image on the canvas
        # We anchor it to North-West (top-left corner) at coordinates 0,0
        canvas.create_image(0, 0, image=main_board, anchor=tk.NW, tags="board")
        
        # IMPORTANT: Keep a reference to the image object.
        # If this variable is garbage collected, the image will vanish from the UI.
        canvas.board_image = main_board

    except Exception as e:
        print(f"Failed to load SVG: {e}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
