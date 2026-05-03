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

    # Loads and centers the game board.
    def draw_board(self):
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

    # Helper to convert config cell math to centered canvas coordinates
    def _get_canvas_coords(self, board_coords):
        # Calculate the top-left offset of the board image
        display_board_size = config.BOARD_SIZE / self.scale
        offset_x = (self.screen_w - display_board_size) / 2
        offset_y = (self.screen_h - display_board_size) / 2

        raw_x, raw_y = board_coords
        return (raw_x / self.scale) + offset_x, (raw_y / self.scale) + offset_y

    # Loads and places all game actors (king, attackers, defenders) on the board
    def set_actors(self):
        assets_dir = os.path.join(config.CURRENT_DIR, "assets")

        # Helper function to load and place an actor
        def place_actor(image_filename, position, tag):
            image_path = os.path.join(assets_dir, image_filename)
            try:
                # Convert SVG to PIL Image
                png_data = cairosvg.svg2png(url=image_path)
                img = Image.open(io.BytesIO(png_data)).convert("RGBA")
                # Resize to ACTOR_SIZE
                img = img.resize(
                    (int(config.ACTOR_SIZE / 1.2), int(config.ACTOR_SIZE / 1.2)),
                    Image.LANCZOS,
                )
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
        idx = 1
        for pos in config.ATTACKERS_POSITIONS.values():
            place_actor("Attacker.svg", pos, f"attacker_{idx}")
            idx = idx + 1
        print()
        # Place defenders
        idx = 1
        for pos in config.DEFENDER_POSITIONS.values():
            place_actor("Defender.svg", pos, f"defender_{idx}")
            idx = idx + 1


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
