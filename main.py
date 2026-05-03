import tkinter as tk
import config
from PIL import Image, ImageTk
import pyglet
import os
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM


class HnefataflGame:
    def __init__(self, root):
        self.root = root
        self.canvas = None
        self.images = {}  # Store references to prevent garbage collection

        # Calculate scaling
        self.screen_w = root.winfo_screenwidth()
        self.screen_h = root.winfo_screenheight()
        fit_size = min(self.screen_w, self.screen_h)
        self.scale = config.BOARD_SIZE / fit_size
        self.actor_display_size = int(config.ACTOR_SIZE / self.scale)

        self.setup_ui()
        self.draw_board()
        self.set_actors()

    def setup_ui(self):
        """Initializes the canvas and basic window properties."""
        self.root.title("Hnefatafl Game")
        self.root.geometry(f"{self.screen_w}x{self.screen_h}")

        icon_path = os.path.join(config.CURRENT_DIR, "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        self.canvas = tk.Canvas(
            self.root,
            width=self.screen_w,
            height=self.screen_h,
            highlightthickness=0,
            bg="#F5EDDA",
        )
        self.canvas.pack(fill="both", expand=True)

    def draw_board(self):
        """Loads and centers the game board."""
        board_path = os.path.join(config.CURRENT_DIR, "assets", "GameBoard.png")
        try:
            img = Image.open(board_path)
            display_size = int(config.BOARD_SIZE / self.scale)
            img = img.resize((display_size, display_size), Image.LANCZOS)

            self.images["board"] = ImageTk.PhotoImage(img)

            # Center calculation
            self.root.update_idletasks()
            titlebar_h = self.root.winfo_rooty() - self.root.winfo_y()

            self.canvas.create_image(
                self.screen_w // 2,
                self.screen_h // 2 - titlebar_h // 2,
                image=self.images["board"],
                anchor=tk.CENTER,
                tags="board",
            )
        except Exception as e:
            print(f"Error loading board: {e}")

    def _get_canvas_coords(self, board_coords):
        """Helper to convert config cell math to centered canvas coordinates."""
        # Calculate the top-left offset of the board image
        display_board_size = config.BOARD_SIZE / self.scale
        offset_x = (self.screen_w - display_board_size) / 2
        offset_y = (self.screen_h - display_board_size) / 2

        raw_x, raw_y = board_coords
        return (raw_x / self.scale) + offset_x, (raw_y / self.scale) + offset_y

    def set_actors(self):
        """Loads and places all game actors (king, attackers, defenders) on the board."""
        assets_dir = os.path.join(config.CURRENT_DIR, "assets")
        
        # Helper function to load and place an actor
        def place_actor(image_filename, position, tag):
            image_path = os.path.join(assets_dir, image_filename)
            try:
                # Convert SVG to PIL Image
                drawing = svg2rlg(image_path)
                img = renderPM.drawToPIL(drawing)
                
                # Resize to ACTOR_SIZE
                img = img.resize((config.ACTOR_SIZE, config.ACTOR_SIZE), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # Store reference to prevent garbage collection
                self.images[tag] = photo
                
                # Convert board coordinates to canvas coordinates
                canvas_x, canvas_y = self._get_canvas_coords(position)
                
                self.canvas.create_image(
                    canvas_x,
                    canvas_y,
                    image=photo,
                    anchor=tk.CENTER,
                    tags=tag,
                )
            except Exception as e:
                print(f"Error loading {image_filename}: {e}")
        
        # Place the king
        place_actor("king.svg", config.KING_POSITION, "king")
        
        # Place attackers
        for pos in config.ATTACKERS_POSITIONS.values():
            place_actor("Attacker.svg", pos, "attacker")
        
        # Place defenders
        for pos in config.DEFENDER_POSITIONS.values():
            place_actor("Defender.svg", pos, "defender")
        


def play_background_music():
    audio_path = os.path.join(config.CURRENT_DIR, "assets", "audio", "Nordic-Folk.ogg")
    try:
        music = pyglet.media.load(audio_path, streaming=False)
        player = pyglet.media.Player()
        player.queue(music)
        player.loop = True
        player.play()
        return player
    except Exception as e:
        print(f"Audio Error: {e}")
        return None


def main():
    root = tk.Tk()

    # Initialize Game Engine
    game = HnefataflGame(root)

    # Audio Setup
    player = play_background_music()

    def update_audio():
        pyglet.clock.tick()
        root.after(10, update_audio)

    if player:
        update_audio()

    root.mainloop()


if __name__ == "__main__":
    main()

# def play_background_music():
#     audio_file = os.path.join(config.CURRENT_DIR, "assets", "audio", "Nordic-Folk.ogg")
#     print(audio_file)
#     music = pyglet.media.load(audio_file, streaming=False)
#     player = pyglet.media.Player()
#     player.queue(music)
#     player.loop = True
#     player.play()

#     return player


# def main():
#     # set the main board
#     root = tk.Tk()
#     root.title("Hnefatafl Game")

#     # used dimensions
#     screen_w = root.winfo_screenwidth()  # approximatly = 1024 * 16/9
#     screen_h = root.winfo_screenheight()

#     fit_size = min(screen_w, screen_h)
#     scale = config.BOARD_SIZE / fit_size
#     root.geometry(f"{screen_w}x{screen_h}")

#     # used paths
#     icon_path = os.path.join(config.CURRENT_DIR, "assets", "icon.ico")
#     board_path = os.path.join(config.CURRENT_DIR, "assets", "GameBoard.png")

#     # verfy file exists to avoid crashes
#     if not os.path.exists(board_path):
#         print(f"Error: couldn't find the path: {board_path}")
#         return

#     # customize icon
#     root.iconbitmap(icon_path)

#     # create the canvas
#     canvas = tk.Canvas(
#         root,
#         width=screen_w,
#         height=screen_h,
#         highlightthickness=0,
#         bg="#F5EDDA",
#     )  # to be with screen's width
#     canvas.pack(fill="both", expand=True)

#     # load the png file (GameBoard)
#     try:
#         board_img = Image.open(board_path).resize(
#             (int(config.BOARD_SIZE / scale), int(config.BOARD_SIZE / scale)),
#             Image.LANCZOS,
#         )

#         # Convert to be as Tkinter Image
#         main_board = ImageTk.PhotoImage(board_img)

#         # place the image to be centered

#         root.update_idletasks()
#         titlebar_h = root.winfo_rooty() - root.winfo_y()
#         canvas.create_image(
#             screen_w // 2,
#             screen_h // 2 - titlebar_h // 2,
#             image=main_board,
#             anchor=tk.CENTER,
#             tags="board",
#         )

#         # ref to the canvas
#         canvas.board_image = main_board

#     except Exception as e:
#         print(f"Faild to load PNG: {e}")

#     player = play_background_music()
#     def update_audio():
#         pyglet.clock.tick()
#         root.after(10, update_audio)

#     update_audio()
#     root.mainloop()


# if __name__ == "__main__":
#     main()
