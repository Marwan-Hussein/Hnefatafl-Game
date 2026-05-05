import vlc
import os
from config import EFFECTS, ASSETS_DIR

# create ONE VLC instance
instance = vlc.Instance("--input-repeat=-1")  # infinite loop

# global player for background music
music_player = instance.media_player_new()


def play_background_music():
    try:
        audio_path = os.path.join(ASSETS_DIR, "audio", "Nordic-Folk.ogg")

        media = instance.media_new(audio_path)
        music_player.set_media(media)

        music_player.play()

    except Exception as e:
        print(f"Audio Error: {e}")


def play_effect(effect_name):
    try:
        effect_path = os.path.join(EFFECTS, effect_name)

        # create a NEW player for each effect (so multiple can overlap)
        effect_player = instance.media_player_new()
        media = instance.media_new(effect_path)

        effect_player.set_media(media)
        effect_player.play()

    except Exception as e:
        print(f"Audio Error: {e}")