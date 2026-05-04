import tkinter as tk
from tkinter import messagebox
import os
import config
from PIL import Image, ImageTk
import pyglet
from canvas import HnefataflGame

class HnefataflHome:
    def __init__(self, root):
        self.root = root
        self.root.title("Hnefatafl - The Viking Game")
        
        # Calculate scaling (same as canvas)
        self.screen_w = root.winfo_screenwidth()
        self.screen_h = root.winfo_screenheight()
        self.root.geometry(f"{self.screen_w}x{self.screen_h}")
        self.root.configure(bg="#1a1a1a") # Dark background for menu

        self.main_frame = tk.Frame(self.root, bg="#1a1a1a")
        self.main_frame.pack(fill="both", expand=True)

        self.selection_data = {
            "mode": None, # HvH or HvC
            "difficulty": None, # Easy, Medium, Hard
            "side": None # Attacker or Defender
        }

        self.setup_ui()
        self.play_music()

    def setup_ui(self):
        # Background Logo or Title
        title_label = tk.Label(
            self.main_frame, 
            text="HNEFATAFL", 
            font=("Georgia", 72, "bold"), 
            fg="#D4AF37", 
            bg="#1a1a1a",
            pady=50
        )
        title_label.pack()

        subtitle_label = tk.Label(
            self.main_frame, 
            text="The Ancient Nordic Board Game", 
            font=("Georgia", 24, "italic"), 
            fg="#F5EDDA", 
            bg="#1a1a1a",
            pady=20
        )
        subtitle_label.pack()

        self.menu_container = tk.Frame(self.main_frame, bg="#1a1a1a")
        self.menu_container.pack(pady=30)

        self.show_main_menu()

    def create_button(self, parent, text, command, width=25):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Georgia", 16, "bold"),
            bg="#2F4F4F",
            fg="#F5EDDA",
            activebackground="#55D7C8",
            activeforeground="#1a1a1a",
            width=width,
            height=2,
            bd=0,
            cursor="hand2"
        )

    def show_main_menu(self):
        self.clear_menu()
        
        btn_hvh = self.create_button(self.menu_container, "Human vs Human", self.select_hvh)
        btn_hvh.pack(pady=10)

        btn_hvc = self.create_button(self.menu_container, "Human vs Computer", self.select_hvc)
        btn_hvc.pack(pady=10)

    def select_hvh(self):
        self.selection_data["mode"] = "HvH"
        self.show_side_selection()

    def select_hvc(self):
        self.selection_data["mode"] = "HvC"
        self.show_difficulty_selection()

    def show_difficulty_selection(self):
        self.clear_menu()
        
        label = tk.Label(self.menu_container, text="Select Difficulty", font=("Georgia", 18), fg="#F5EDDA", bg="#1a1a1a", pady=10)
        label.pack()

        difficulties = ["Easy", "Medium", "Hard"]
        for diff in difficulties:
            btn = self.create_button(self.menu_container, diff, lambda d=diff: self.set_difficulty(d))
            btn.pack(pady=5)
            
        btn_back = self.create_button(self.menu_container, "Back", self.show_main_menu, width=15)
        btn_back.configure(bg="#4a4a4a")
        btn_back.pack(pady=20)

    def set_difficulty(self, diff):
        self.selection_data["difficulty"] = diff
        self.show_side_selection()

    def show_side_selection(self):
        self.clear_menu()
        
        mode_text = "Player 1: Select Side" if self.selection_data["mode"] == "HvH" else "Select Your Side"
        label = tk.Label(self.menu_container, text=mode_text, font=("Georgia", 18), fg="#F5EDDA", bg="#1a1a1a", pady=10)
        label.pack()

        btn_attacker = self.create_button(self.menu_container, "Attacker", lambda: self.start_game("attacker"))
        btn_attacker.pack(pady=5)

        defender_text = "Defender" if self.selection_data["mode"] == "HvH" else "Defender with King"
        btn_defender = self.create_button(self.menu_container, defender_text, lambda: self.start_game("defender"))
        btn_defender.pack(pady=5)
        
        back_cmd = self.show_difficulty_selection if self.selection_data["mode"] == "HvC" else self.show_main_menu
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
        HnefataflGame(self.root, self.selection_data)

    def play_music(self):
        audio_path = os.path.join(config.ASSETS_DIR, "audio", "Nordic-Folk.ogg")
        try:
            music = pyglet.media.load(audio_path, streaming=False)
            self.player = pyglet.media.Player()
            self.player.queue(music)
            self.player.loop = True
            self.player.play()

            def update_audio():
                pyglet.clock.tick()
                self.root.after(10, update_audio)

            update_audio()
        except Exception as e:
            print(f"Audio Error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    # Icon
    icon_path = os.path.join(config.ASSETS_DIR, "icon.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
        
    app = HnefataflHome(root)
    root.mainloop()
