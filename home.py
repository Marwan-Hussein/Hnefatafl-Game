import tkinter as tk
from tkinter import messagebox
import os
import config
from PIL import Image, ImageTk
import pyglet
from canvas import HnefataflGame
from audio_player import *

back_ground_color = "#F5EDDA"
dark_red = "#860F0F"


class HnefataflHome:
    def __init__(self, root):
        self.root = root
        self.root.title("Hnefatafl - The Viking Game")
        self.current_game = None
        self.player = None
        self.audio_loop_running = False
        self.root.protocol("WM_DELETE_WINDOW", self.handle_app_close)

        # Calculate scaling (same as canvas)]
        self.screen_w = root.winfo_screenwidth()
        self.screen_h = root.winfo_screenheight()
        self.root.geometry(f"{self.screen_w}x{self.screen_h}")
        self.root.configure(bg=back_ground_color)  # Dark background for menu

        self.main_frame = tk.Frame(self.root, bg=back_ground_color)
        self.main_frame.pack(fill="both", expand=True)

        self.selection_data = {
            "mode": None,  # HvH or HvC
            "difficulty": None,  # Easy, Medium, Hard
            "side": None,  # Attacker or Defender
        }

        self.setup_ui()
        # self.play_music()
        play_background_music()

    def setup_ui(self):
        # Background Logo or Title
        title_label = tk.Label(
            self.main_frame,
            text="HNEFATAFL",
            font=("Georgia", 72, "bold"),
            fg="#C1A031",
            bg=back_ground_color,
            pady=50,
        )
        title_label.pack()

        subtitle_label = tk.Label(
            self.main_frame,
            text="The Ancient Nordic Board Game",
            font=("Georgia", 24, "italic"),
            fg=dark_red,
            bg=back_ground_color,
            pady=20,
        )
        subtitle_label.pack()

        self.menu_container = tk.Frame(self.main_frame, bg=back_ground_color)
        self.menu_container.pack(pady=30)

        self.show_main_menu()

    def create_button(self, parent, text, command, width=25):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Georgia", 16, "bold"),
            bg=dark_red,
            fg=back_ground_color,
            activebackground="#B11616",
            activeforeground=back_ground_color,
            width=width,
            height=2,
            bd=0,
            cursor="hand2",
        )

    def show_main_menu(self):
        self.clear_menu()

        btn_hvh = self.create_button(
            self.menu_container, "Human vs Human", self.select_hvh
        )
        btn_hvh.pack(pady=10)

        btn_hvc = self.create_button(
            self.menu_container, "Human vs Computer", self.select_hvc
        )
        btn_hvc.pack(pady=10)

    def select_hvh(self):
        self.selection_data["mode"] = "HvH"
        self.start_game("attacker")

    def select_hvc(self):
        self.selection_data["mode"] = "HvC"
        self.show_difficulty_selection()

    def show_difficulty_selection(self):
        self.clear_menu()

        label = tk.Label(
            self.menu_container,
            text="Select Difficulty",
            font=("Georgia", 18),
            fg=back_ground_color,
            bg=back_ground_color,
            pady=10,
        )
        label.pack()

        difficulties = ["Easy", "Medium", "Hard"]
        for diff in difficulties:
            btn = self.create_button(
                self.menu_container, diff, lambda d=diff: self.set_difficulty(d)
            )
            btn.pack(pady=5)

        btn_back = self.create_button(
            self.menu_container, "Back", self.show_main_menu, width=15
        )
        btn_back.configure(bg="#4a4a4a")
        btn_back.pack(pady=20)

    def set_difficulty(self, diff):
        self.selection_data["difficulty"] = diff
        self.show_side_selection()

    def show_side_selection(self):
        self.clear_menu()

        mode_text = (
            "Player 1: Select Side"
            if self.selection_data["mode"] == "HvH"
            else "Select Your Side"
        )
        label = tk.Label(
            self.menu_container,
            text=mode_text,
            font=("Georgia", 18),
            fg=back_ground_color,
            bg=back_ground_color,
            pady=10,
        )
        label.pack()

        btn_attacker = self.create_button(
            self.menu_container, "Attacker", lambda: self.start_game("attacker")
        )
        btn_attacker.pack(pady=5)

        defender_text = (
            "Defender" if self.selection_data["mode"] == "HvH" else "Defender with King"
        )
        btn_defender = self.create_button(
            self.menu_container, defender_text, lambda: self.start_game("defender")
        )
        btn_defender.pack(pady=5)

        back_cmd = (
            self.show_difficulty_selection
            if self.selection_data["mode"] == "HvC"
            else self.show_main_menu
        )
        btn_back = self.create_button(self.menu_container, "Back", back_cmd, width=15)
        btn_back.configure(bg="#4a4a4a")
        btn_back.pack(pady=20)

    def clear_menu(self):
        for widget in self.menu_container.winfo_children():
            widget.destroy()

    def start_game(self, side):
        self.selection_data["side"] = side
        # Transition to game
        self.main_frame.destroy()

        # Initialize Game in the root with settings
        self.current_game = HnefataflGame(
            self.root,
            self.selection_data.copy(),
            on_game_end=self.return_to_home,
        )

    def return_to_home(self):
        if self.current_game:
            self.current_game.destroy_ui()
            self.current_game = None

        self.selection_data = {"mode": None, "difficulty": None, "side": None}

        self.main_frame = tk.Frame(self.root, bg=back_ground_color)
        self.main_frame.pack(fill="both", expand=True)
        self.setup_ui()

    def play_music(self):
        if self.player is not None:
            return

        audio_path = os.path.join(config.ASSETS_DIR, "audio", "Nordic-Folk.ogg")
        try:
            music = pyglet.media.load(audio_path, streaming=False)
            self.player = pyglet.media.Player()
            self.player.queue(music)

            @self.player.event
            def on_eos():
                self.player.seek(0)
                self.player.play()

            self.player.play()
            self.start_audio_loop()
        except Exception as e:
            print(f"Audio Error: {e}")

    def start_audio_loop(self):
        if self.audio_loop_running:
            return

        self.audio_loop_running = True

        def update_audio():
            if not self.audio_loop_running:
                return
            pyglet.clock.tick()
            self.root.after(10, update_audio)

        update_audio()

    def stop_music(self):
        self.audio_loop_running = False
        if self.player is not None:
            try:
                self.player.pause()
                self.player.delete()
            except Exception:
                pass
            self.player = None

    def handle_app_close(self):
        self.stop_music()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    # Icon
    icon_path = os.path.join(config.ASSETS_DIR, "icon.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)

    app = HnefataflHome(root)
    root.mainloop()
