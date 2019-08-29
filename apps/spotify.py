from talon import applescript
from talon.voice import Context, Key


def spotify(thing):
    def _spotify(*_):
        applescript.run(f'tell application "Spotify" to {thing}')

    return _spotify


ctx = Context("spotify")
ctx.keymap(
    {
        "pause song": spotify("pause"),
        "play song": spotify("play"),
        "next song": spotify("next track"),
        "last song": spotify("previous track"),
    }
)
