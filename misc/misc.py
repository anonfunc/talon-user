import subprocess

from talon.voice import Context, Key

from ..utils import text

ctx = Context("misc")

ctx.keymap(
    {
        "go dark": lambda _: subprocess.check_call(
            ["open", "/System/Library/CoreServices/ScreenSaverEngine.app"]
        )
    }
)

ctx = Context("shortcat")

ctx.keymap(
    {
        "(shortcat | short cap | shortcut) [<dgndictation>]": [
            Key("cmd+shift+ctrl+f14"),
            text,
        ]
    }
)
