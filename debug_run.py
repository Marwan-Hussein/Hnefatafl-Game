
import traceback
import sys

print("Starting debug script...")
try:
    print("Importing tkinter...")
    import tkinter as tk
    print("Importing config...")
    import config
    print("Importing PIL...")
    from PIL import Image, ImageTk
    print("Importing audio_player...")
    import audio_player
    print("Importing canvas...")
    import canvas
    print("Importing home...")
    import home
    print("All imports successful")
    
    root = tk.Tk()
    app = home.HnefataflHome(root)
    print("App initialized")
    root.mainloop()
except Exception as e:
    print("Caught Exception:")
    traceback.print_exc()
