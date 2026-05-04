import tkinter as tk
import config
from PIL import Image, ImageTk
import cairosvg
import io
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

    # Initializes the canvas and basic window properties.
    def setup_ui(self):
        self.root.title("Hnefatafl Game")
        self.root.geometry(f"{self.screen_w}x{self.screen_h}")

        icon_path = os.path.join(config.ASSETS_DIR, "icon.ico")
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
        self.canvas.bind("<Button-1>", self.on_board_click)

    """ Calculates which cell (i, j) was clicked """

    def on_board_click(self, event):
        # delete all existing dots if there is
        for tag in list(self.images.keys()):
            if tag.startswith("dot_"):
                self.canvas.delete(tag)
                del self.images[tag]

        # 1. Get board display size and offsets
        display_board_size = config.BOARD_SIZE / self.scale
        offset_x = (self.screen_w - display_board_size) / 2
        offset_y = (self.screen_h - display_board_size) / 2

        # 2. Check if click is actually inside the board boundaries
        if (
            offset_x <= event.x <= offset_x + display_board_size
            and offset_y <= event.y <= offset_y + display_board_size
        ):

            # 3. Convert screen click to 'board' coordinates
            relative_x = (event.x - offset_x) * self.scale
            relative_y = (event.y - offset_y) * self.scale

            # taking care about the internal offset used by config.cell()
            grid_x = relative_x - (config.internal_offset + 2)
            grid_y = relative_y - (config.internal_offset - 20)

            # 4. Convert coordinates to Grid Index (i, j)
            i = int(round(grid_x / config.CELL_SIZE))
            j = int(round(grid_y / config.CELL_SIZE))

            if not self.is_inside_board(i, j):
                return

            print(f"Clicked Cell: ({i}, {j})")

            # printing dots in avaialable positions
            if config.OCCUPIED_CELLS[i][j] == 0:
                self.highlight_cell(
                    i, j
                )  # optional: Visual feedback (highlighting the cell)
                self.show_available_moves(i, j)

    def is_inside_board(self, i, j):
        return 0 <= i < config.BOARD_CELLS and 0 <= j < config.BOARD_CELLS

    def show_available_moves(self, start_i, start_j):
        directions = (
            (0, 1),  # down
            (0, -1),  # up
            (1, 0),  # right
            (-1, 0),  # left
        )

        for di, dj in directions:
            i = start_i + di
            j = start_j + dj

            while self.is_inside_board(i, j):
                if config.OCCUPIED_CELLS[i][j] == 0 or (i, j) in config.CORNERS:
                    break

                self.place_actor("dot.svg", config.cell(i, j), f"dot_{i}_{j}", 50)
                i += di
                j += dj

    """ Draws a temporary rectangle to show selection"""

    def highlight_cell(self, i, j):
        self.canvas.delete("highlight")  # Clear previous highlight

        x, y = self._get_canvas_coords(config.cell(i + 2, j + 2))
        x, y = x - config.internal_offset, y - config.internal_offset
        size = config.CELL_SIZE / self.scale

        self.canvas.create_rectangle(
            x, y, x + size, y + size, outline="#55D7C8", width=3, tags="highlight"
        )

    # Loads and centers the game board.
    def draw_board(self):
        board_path = os.path.join(config.ASSETS_DIR, "GameBoard.png")
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

    # Helper to convert config cell math to centered canvas coordinates
    def _get_canvas_coords(self, board_coords):
        # Calculate the top-left offset of the board image
        display_board_size = config.BOARD_SIZE / self.scale
        offset_x = (self.screen_w - display_board_size) / 2
        offset_y = (self.screen_h - display_board_size) / 2

        raw_x, raw_y = board_coords
        return (raw_x / self.scale) + offset_x, (raw_y / self.scale) + offset_y

    # Helper function to load and place an actor
    def place_actor(
        self, image_filename, position, tag, size=int(config.ACTOR_SIZE / 1.2)
    ):
        image_path = os.path.join(config.ASSETS_DIR, image_filename)
        try:
            # Convert SVG to PIL Image
            png_data = cairosvg.svg2png(url=image_path)
            img = Image.open(io.BytesIO(png_data)).convert("RGBA")
            # Resize to ACTOR_SIZE
            img = img.resize((size, size), Image.LANCZOS)
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

    # Loads and places all game actors (king, attackers, defenders) on the board
    def set_actors(self):
        assets_dir = os.path.join(config.ASSETS_DIR)

        # Place the king
        self.place_actor("king.svg", config.KING_POSITION, "king")

        # Place attackers
        idx = 1
        for pos in config.ATTACKERS_POSITIONS.values():
            self.place_actor("Attacker.svg", pos, f"attacker_{idx}")
            idx = idx + 1
        print()
        # Place defenders
        idx = 1
        for pos in config.DEFENDER_POSITIONS.values():
            self.place_actor("Defender.svg", pos, f"defender_{idx}")
            idx = idx + 1


def play_background_music():
    audio_path = os.path.join(config.ASSETS_DIR, "audio", "Nordic-Folk.ogg")
    try:
        music = pyglet.media.load(audio_path, streaming=False)
        player = pyglet.media.Player()
        player.queue(music)
        player.loop = True

        @player.event
        def on_eos():
            player.seek(0)
            player.play()

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


main()
