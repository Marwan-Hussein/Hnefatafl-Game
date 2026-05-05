import vlc
import time
import os
from config import EFFECTS, ASSETS_DIR

def play_background_music():
    try:
        audio_path = os.path.join(ASSETS_DIR, "audio", "Nordic-Folk.ogg")
        player = vlc.MediaPlayer(audio_path)

        player.play()

        # loop manually
        while True:
            if player.get_state() == vlc.State.Ended:
                player.stop()
                player.play()
            time.sleep(1)
    except Exception as e:
        print(f"Audio Error: {e}")


def play_effect(effect_name):
    try:
        effect_path = os.path.join(EFFECTS, effect_name)
        player = vlc.MediaPlayer(effect_path)

        player.play()

    except Exception as e:
        print(f"Audio Error: {e}")
