import tkinter as tk
import config
from PIL import Image, ImageTk
import cairosvg
import io
import pyglet
import os
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from game_logic.Game.constants import ATTACKER, DEFENDER, EMPTY, KING
from game_logic.Game.moves import apply_move, get_all_moves, get_piece_moves
from game_logic.Game.rules import apply_captures, check_winner
from game_logic.Game.state import GameState
from game_logic.AI.alphabeta import get_best_move

attacker_color = "#1C1D17"
defender_color = "#BDA160"
dark_red = "#860F0F"


class HnefataflGame:
    def __init__(self, root, settings=None, on_game_end=None):
        self.root = root
        self.settings = settings
        self.on_game_end = on_game_end
        self.canvas = None
        self.images = {}  # Store references to prevent garbage collection
        self.game_state = GameState()

        # Turn logic
        self.current_turn_team = self.game_state.turn
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
        self.ai_turn_pending = False

        self.setup_ui()
        self.draw_board()
        self.set_actors()
        self.update_turn_display()
        self.root.after(150, self.maybe_schedule_ai_turn)

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
        team = self.game_state.turn
        self.current_turn_team = team
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
                    display_text = "Player's Turn"
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
        if self.game_over or self.ai_turn_pending or self.is_ai_turn():
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

        actor_tag = self.cell_actors.get(clicked_cell)
        if actor_tag:
            actor_type = self.get_actor_type(actor_tag)
            team = (
                "defender"
                if (actor_type == "defender" or actor_type == "king")
                else "attacker"
            )

            if team == self.game_state.turn:
                self.select_actor(actor_tag, clicked_cell)
            else:
                print(f"It's {self.game_state.turn}'s turn!")

    def is_inside_board(self, i, j):
        return 0 <= i < config.BOARD_CELLS and 0 <= j < config.BOARD_CELLS

    def gui_to_logic_cell(self, cell):
        col, row = cell
        return row, col

    def logic_to_gui_cell(self, row, col):
        return col, row

    def get_captured_cells(self, previous_board, move):
        fr, fc, tr, tc = move
        captured_cells = []

        for row_idx, row in enumerate(previous_board):
            for col_idx, previous_piece in enumerate(row):
                current_piece = self.game_state.board[row_idx][col_idx]
                if (
                    previous_piece != EMPTY
                    and current_piece == EMPTY
                    and (row_idx, col_idx) != (fr, fc)
                ):
                    captured_cells.append(self.logic_to_gui_cell(row_idx, col_idx))

        if self.game_state.board[tr][tc] == EMPTY:
            captured_cells.append(self.logic_to_gui_cell(tr, tc))

        return captured_cells

    def show_available_moves(self, start_i, start_j):
        move_cells = set()

        start_row, start_col = self.gui_to_logic_cell((start_i, start_j))
        legal_moves = get_piece_moves(self.game_state, start_row, start_col)

        for _, _, target_row, target_col in legal_moves:
            gui_cell = self.logic_to_gui_cell(target_row, target_col)
            self.place_actor(
                "dot.svg",
                config.cell(*gui_cell),
                f"dot_{gui_cell[0]}_{gui_cell[1]}",
                50,
            )
            move_cells.add(gui_cell)

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

        if old_cell == new_cell or new_cell not in self.available_move_cells:
            return

        old_row, old_col = self.gui_to_logic_cell(old_cell)
        new_row, new_col = self.gui_to_logic_cell(new_cell)
        move = (old_row, old_col, new_row, new_col)
        self.execute_move(move)

    def is_human_vs_computer(self):
        return bool(self.settings) and self.settings.get("mode") == "HvC"

    def get_human_side(self):
        if not self.is_human_vs_computer():
            return None
        return self.settings.get("side")

    def get_ai_side(self):
        human_side = self.get_human_side()
        if human_side == "attacker":
            return "defender"
        if human_side == "defender":
            return "attacker"
        return None

    def is_ai_turn(self):
        return self.is_human_vs_computer() and self.game_state.turn == self.get_ai_side()

    def maybe_schedule_ai_turn(self):
        if self.game_over or self.ai_turn_pending or not self.is_ai_turn():
            return

        self.ai_turn_pending = True
        self.root.after(150, self.play_ai_turn)

    def ensure_current_player_can_move(self):
        legal_moves = get_all_moves(self.game_state, self.game_state.turn)
        if legal_moves:
            return True

        winner = "defender" if self.game_state.turn == "attacker" else "attacker"
        self.end_game(winner)
        return False

    def execute_move(self, move):
        old_row, old_col, new_row, new_col = move
        old_cell = self.logic_to_gui_cell(old_row, old_col)
        new_cell = self.logic_to_gui_cell(new_row, new_col)
        actor_tag = self.cell_actors.get(old_cell)

        if actor_tag is None:
            print(f"No actor found at {old_cell} for move {move}")
            self.clear_selection()
            return

        previous_board = [row[:] for row in self.game_state.board]

        apply_move(self.game_state, move)
        apply_captures(self.game_state, move)

        captured_cells = self.get_captured_cells(previous_board, move)
        moved_piece_survived = self.game_state.board[new_row][new_col] != EMPTY

        self.cell_actors.pop(old_cell, None)

        if moved_piece_survived:
            new_x, new_y = self._get_canvas_coords(config.cell(*new_cell))
            self.canvas.coords(actor_tag, new_x, new_y)
            self.actor_cells[actor_tag] = new_cell
            self.cell_actors[new_cell] = actor_tag
        else:
            self.canvas.delete(actor_tag)
            self.actor_cells.pop(actor_tag, None)

        print(f"Moved {actor_tag}: {(old_row, old_col)} -> {(new_row, new_col)}")
        self.clear_selection()

        for cell in captured_cells:
            if cell == new_cell and not moved_piece_survived:
                continue
            tag = self.cell_actors.pop(cell, None)
            if tag:
                self.canvas.delete(tag)
                if tag in self.actor_cells:
                    del self.actor_cells[tag]

        winner = check_winner(self.game_state)
        if winner:
            self.end_game(winner)
            return

        self.game_state.switch_turn()
        self.current_turn_team = self.game_state.turn

        if not self.ensure_current_player_can_move():
            return

        self.update_turn_display()
        self.maybe_schedule_ai_turn()

    def play_ai_turn(self):
        self.ai_turn_pending = False

        if self.game_over or not self.is_ai_turn():
            return

        if not self.ensure_current_player_can_move():
            return

        difficulty = (self.settings or {}).get("difficulty", "medium")
        move = get_best_move(self.game_state, self.game_state.turn, difficulty)

        if move is None:
            winner = "defender" if self.game_state.turn == "attacker" else "attacker"
            self.end_game(winner)
            return

        self.execute_move(move)

    def end_game(self, winner):
        self.game_over = True
        self.clear_selection()
        self.display_winner(winner)
        if self.on_game_end:
            self.root.after(2500, self.on_game_end)

    def display_winner(self, team):
        winner_name = team.capitalize()
        text = f"Game Over: {winner_name} Wins"
        detail_text = "This match has ended."
        accent_color = attacker_color if team == "attacker" else defender_color

        self.canvas.delete("winner_ui")
        box_w = 640
        box_h = 170
        x1 = (self.screen_w - box_w) // 2
        y1 = (self.screen_h - box_h) // 2
        x2 = x1 + box_w
        y2 = y1 + box_h

        self.canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill="#F5EDDA",
            outline=accent_color,
            width=4,
            tags="winner_ui",
        )
        self.canvas.create_text(
            self.screen_w // 2,
            self.screen_h // 2 - 22,
            text=text,
            font=("Georgia", 48, "bold"),
            fill=dark_red,
            tags="winner_ui",
        )
        self.canvas.create_text(
            self.screen_w // 2,
            self.screen_h // 2 + 28,
            text=detail_text,
            font=("Georgia", 22, "bold"),
            fill=accent_color,
            tags="winner_ui",
        )
        self.turn_label.config(text=f"{text} - Match Ended", fg=dark_red)

    def destroy_ui(self):
        if self.canvas is not None and self.canvas.winfo_exists():
            self.canvas.destroy()
            self.canvas = None
        if self.turn_label is not None and self.turn_label.winfo_exists():
            self.turn_label.destroy()
            self.turn_label = None

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
        self.actor_cells.clear()
        self.cell_actors.clear()

        attacker_idx = 1
        defender_idx = 1

        for row_idx, row in enumerate(self.game_state.board):
            for col_idx, piece in enumerate(row):
                if piece == EMPTY:
                    continue

                gui_cell = self.logic_to_gui_cell(row_idx, col_idx)
                position = config.cell(*gui_cell)

                if piece == KING:
                    tag = "king"
                    image_filename = "king.svg"
                elif piece == ATTACKER:
                    tag = f"attacker_{attacker_idx}"
                    image_filename = "Attacker.svg"
                    attacker_idx += 1
                else:
                    tag = f"defender_{defender_idx}"
                    image_filename = "Defender.svg"
                    defender_idx += 1

                self.place_actor(image_filename, position, tag)
                self.actor_cells[tag] = gui_cell
                self.cell_actors[gui_cell] = tag


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
