import tkinter as tk
import config
from PIL import Image, ImageTk
import cairosvg
import io
import pyglet
import os
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

attacker_color = "#1C1D17"
defender_color = "#BDA160"
dark_red = "#860F0F"


class HnefataflGame:
    def __init__(self, root, settings=None):
        self.root = root
        self.settings = settings
        self.canvas = None
        self.images = {}  # Store references to prevent garbage collection

        # Turn logic
        self.current_turn_team = "attacker"  # Attackers usually start
        self.turn_label = None

        # Calculate scaling
        self.screen_w = root.winfo_screenwidth()
        self.screen_h = root.winfo_screenheight()
        fit_size = min(self.screen_w, self.screen_h)
        self.scale = config.BOARD_SIZE / fit_size
        self.actor_display_size = int(config.ACTOR_SIZE / self.scale)
        self.clicked = False
        self.selected_actor_tag = None
        self.selected_actor_cell = None
        self.available_move_cells = set()
        self.actor_cells = {}
        self.cell_actors = {}
        self.game_over = False

        self.setup_ui()
        self.draw_board()
        self.set_actors()
        self.update_turn_display()

    # Initializes the canvas and basic window properties.
    def setup_ui(self):
        self.root.title("Hnefatafl Game")
        self.root.geometry(f"{self.screen_w}x{self.screen_h}")

        icon_path = os.path.join(config.ASSETS_DIR, "icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        # Turn Indicator Label
        self.turn_label = tk.Label(
            self.root,
            text="",
            font=("Georgia", 24, "bold"),
            bg="#F5EDDA",
            fg="#2F4F4F",
            pady=10,
        )
        self.turn_label.pack(side="bottom", fill="x")

        self.canvas = tk.Canvas(
            self.root,
            width=self.screen_w,
            height=self.screen_h,
            highlightthickness=0,
            bg="#F5EDDA",
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_board_click)

    def update_turn_display(self):
        team = self.current_turn_team
        display_text = ""

        if not self.settings:
            display_text = f"{team.capitalize()}'s Turn"
        else:
            mode = self.settings.get("mode")
            player_side = self.settings.get("side")

            if mode == "HvH":
                if team == player_side:
                    display_text = f"Player 1's Turn [{team.capitalize()}]"
                else:
                    display_text = f"Player 2's Turn [{team.capitalize()}]"
            elif mode == "HvC":
                if team == player_side:
                    display_text = "Actor's Turn"
                else:
                    display_text = "Computer's Turn"
            else:
                display_text = f"{team.capitalize()}'s Turn"

        self.turn_label.config(text=display_text)
        # Update color based on team
        if team == "attacker":
            self.turn_label.config(fg=attacker_color)  # Dark Red for attackers
        else:
            self.turn_label.config(fg=defender_color)  # Dark Blue for defenders

    """delete all existing dots if there is"""

    def delete_existing_dots(self):
        for tag in list(self.images.keys()):
            if tag.startswith("dot_"):
                self.canvas.delete(tag)
                del self.images[tag]

    """ Calculates which cell (i, j) was clicked """

    def get_clicked_cell(self, event):
        # 1. Get board display size and offsets
        display_board_size = config.BOARD_SIZE / self.scale
        offset_x = (self.screen_w - display_board_size) / 2
        offset_y = (self.screen_h - display_board_size) / 2

        # 2. Check if click is actually inside the board boundaries
        if not (
            offset_x <= event.x <= offset_x + display_board_size
            and offset_y <= event.y <= offset_y + display_board_size
        ):
            return None

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
            return None

        return i, j

    def on_board_click(self, event):
        if self.game_over:
            return

        clicked_cell = self.get_clicked_cell(event)
        if clicked_cell is None:
            return

        i, j = clicked_cell
        print(f"Clicked Cell: ({j}, {i})")

        if (
            self.selected_actor_tag
            and clicked_cell in self.available_move_cells
            and clicked_cell != self.selected_actor_cell
        ):
            self.move_selected_actor(clicked_cell)
            return

        self.clear_selection()

        if config.OCCUPIED_CELLS[i][j] == 0:
            actor_tag = self.cell_actors.get(clicked_cell)
            if actor_tag:
                # Check if it's the correct turn's piece
                actor_type = self.get_actor_type(actor_tag)
                # King is always on the defender team
                team = (
                    "defender"
                    if (actor_type == "defender" or actor_type == "king")
                    else "attacker"
                )

                if team == self.current_turn_team:
                    self.select_actor(actor_tag, clicked_cell)
                else:
                    print(f"It's {self.current_turn_team}'s turn!")

    def is_inside_board(self, i, j):
        return 0 <= i < config.BOARD_CELLS and 0 <= j < config.BOARD_CELLS

    def show_available_moves(self, start_i, start_j):
        actor_type = self.get_actor_type(self.selected_actor_tag)
        directions = (
            (0, 1),  # down
            (0, -1),  # up
            (1, 0),  # right
            (-1, 0),  # left
        )

        move_cells = set()

        for di, dj in directions:
            i = start_i + di
            j = start_j + dj

            while self.is_inside_board(i, j):
                # Stop if cell is occupied
                if config.OCCUPIED_CELLS[i][j] == 0:
                    break

                # Stop if cell is a corner and the actor is not the King
                if (i, j) in config.CORNERS and actor_type != "king":
                    break

                self.place_actor("dot.svg", config.cell(i, j), f"dot_{i}_{j}", 50)
                move_cells.add((i, j))
                
                # If the king enters a corner, he can't go past it (though it's usually at the edge anyway)
                if (i, j) in config.CORNERS:
                    break
                    
                i += di
                j += dj

        return move_cells

    def select_actor(self, actor_tag, cell):
        self.selected_actor_tag = actor_tag
        self.selected_actor_cell = cell
        self.clicked = True
        self.highlight_cell(*cell)
        self.available_move_cells = self.show_available_moves(*cell)

    def clear_selection(self):
        self.delete_existing_dots()
        self.canvas.delete("highlight")
        self.clicked = False
        self.selected_actor_tag = None
        self.selected_actor_cell = None
        self.available_move_cells = set()

    def move_selected_actor(self, new_cell):
        old_cell = self.selected_actor_cell
        actor_tag = self.selected_actor_tag

        if old_cell == new_cell or new_cell not in self.available_move_cells:
            return

        actor_type = self.get_actor_type(actor_tag)
        config.update_actor_position(actor_type, old_cell, new_cell)

        new_x, new_y = self._get_canvas_coords(config.cell(*new_cell))
        self.canvas.coords(actor_tag, new_x, new_y)

        self.actor_cells[actor_tag] = new_cell
        self.cell_actors.pop(old_cell, None)
        self.cell_actors[new_cell] = actor_tag

        old_cell = (old_cell[1], old_cell[0])
        new_cell = (new_cell[1], new_cell[0])

        print(f"Moved {actor_tag}: {old_cell} -> {new_cell}")
        self.clear_selection()

        # Rule Processing: Captures and Winner
        # old_cell and new_cell are (i, j) where i is column and j is row?
        # Wait, config.cell(i, j) uses i as col, j as row.
        # But board usually uses (row, col). Let's be consistent with config.
        last_move = (old_cell[0], old_cell[1], new_cell[0], new_cell[1])
        winner, captured_cells = config.process_game_step(last_move)

        for cell in captured_cells:
            tag = self.cell_actors.pop(cell, None)
            if tag:
                self.canvas.delete(tag)
                if tag in self.actor_cells:
                    del self.actor_cells[tag]

        if winner:
            self.display_winner(winner)
            self.game_over = True
            return

        # Switch turns
        self.current_turn_team = (
            "defender" if self.current_turn_team == "attacker" else "attacker"
        )
        self.update_turn_display()

    def display_winner(self, team):
        # PLAYER' WIN [{team.capitalize()}]
        text = f"PLAYER' WIN [{team.capitalize()}]"
        bg_color = attacker_color if team.capitalize() == "ATTACKER" else defender_color
        self.canvas.create_text(
            self.screen_w // 2,
            self.screen_h // 2,
            text=text,
            font=("Georgia", 48, "bold"),
            fill=dark_red,
            bg=bg_color,
            tags="winner_msg",
        )
        self.turn_label.config(text=text, fg=dark_red)

    def get_actor_type(self, actor_tag):
        if actor_tag == "king":
            return "king"
        if actor_tag.startswith("defender_"):
            return "defender"
        if actor_tag.startswith("attacker_"):
            return "attacker"
        return None

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
        self.actor_cells["king"] = config.KING_CELL
        self.cell_actors[config.KING_CELL] = "king"

        # Place attackers
        idx = 1
        for cell, pos in config.ATTACKERS_POSITIONS.items():
            tag = f"attacker_{idx}"
            self.place_actor("Attacker.svg", pos, tag)
            self.actor_cells[tag] = cell
            self.cell_actors[cell] = tag
            idx = idx + 1
        print()
        # Place defenders
        idx = 1
        for cell, pos in config.DEFENDER_POSITIONS.items():
            tag = f"defender_{idx}"
            self.place_actor("Defender.svg", pos, tag)
            self.actor_cells[tag] = cell
            self.cell_actors[cell] = tag
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


if __name__ == "__main__":
    main()
