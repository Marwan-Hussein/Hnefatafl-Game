import os
from config import EFFECTS, ASSETS_DIR
import time
import threading

try:
    import vlc
except ModuleNotFoundError:
    vlc = None

try:
    # create ONE VLC instance
    instance = vlc.Instance() if vlc is not None else None
except Exception:
    instance = None

# global player for background music
music_player = instance.media_player_new() if instance is not None else None
_effect_players = []
_audio_warning_shown = False

EFFECT = {
    "click": "click.mp3",
    "kill": "kill.mp3",
    "loser": "loser.mp3",
    "winner": "winner.mp3",
}


def _warn_audio_unavailable():
    global _audio_warning_shown
    if _audio_warning_shown:
        return
    print("Audio Error: VLC audio support is not available.")
    _audio_warning_shown = True


def _bg_music_loop():
    """handle the looping logic (background music) in a separate thread."""
    try:
        # Use the global music_player we already created at the top of the file
        if instance is None or music_player is None:
            _warn_audio_unavailable()
            return

        audio_path = os.path.join(ASSETS_DIR, "audio", "Nordic-Folk.ogg")
        media = instance.media_new(audio_path)
        music_player.set_media(media)
        music_player.play()

        while True:
            # Check if the music finished
            if music_player.get_state() == vlc.State.Ended:
                music_player.stop()
                music_player.play()
            time.sleep(1)  # Sleep to prevent high CPU usage
    except Exception as e:
        print(f"Audio Error in thread: {e}")


def play_background_music():
    bg_thread = threading.Thread(target=_bg_music_loop, daemon=True)
    bg_thread.start()


def stop_background_music():
    try:
        if music_player is None:
            return
        music_player.stop()
    except Exception as e:
        print(f"Audio Error: {e}")


def _cleanup_effect_players():
    global _effect_players
    _effect_players = [
        player
        for player in _effect_players
        if player.get_state()
        not in (vlc.State.Ended, vlc.State.Error, vlc.State.Stopped)
    ]


def play_effect(effect_name):
    try:
        if instance is None:
            _warn_audio_unavailable()
            return

        effect_path = os.path.join(EFFECTS, effect_name)

        # create a NEW player for each effect (so multiple can overlap)
        effect_player = instance.media_player_new()
        media = instance.media_new(effect_path)

        effect_player.set_media(media)
        effect_player.play()
        _effect_players.append(effect_player)
        _cleanup_effect_players()

    except Exception as e:
        print(f"Audio Error: {e}")
