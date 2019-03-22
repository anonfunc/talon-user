import subprocess
import time

from talon import keychain
from talon.voice import Context, Key

from ..utils import text, select_last_insert, delay

ctx = Context("misc")
ctx.vocab = ["Jira"]
ctx.keymap(
    {
        "launch": Key("cmd-space"),
        "launch <dgndictation> [over]": [Key("cmd-space"), delay(0.4), text],
        "correct": select_last_insert,
        "go dark": lambda _: subprocess.check_call(
            ["open", "/System/Library/CoreServices/ScreenSaverEngine.app"]
        ),
        "go toolbox": Key("cmd+shift+ctrl+f1"),
        "password amigo": keychain.find("login", "user"),
        "snippet [<dgndictation>]": [  # XXX Doesn't really go here
            Key("cmd-shift-j"),
            delay(0.1),
            text,
        ],
        # Clipboard
        "clippings [<dgndictation>]": [
            Key("cmd+ctrl+c"),
            delay(0.1),
            text,
        ],
        "cut this": Key("cmd-x"),
        "copy this": Key("cmd-c"),
        "paste": Key("cmd-v"),
        # Menubar:
        "menubar": Key("ctrl-f2"),
        # Bartender needed for this one
        "menu icons": Key("ctrl-f8"),
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

ctx = Context("login", bundle="com.apple.loginwindow")
ctx.keymap({"amigo": [keychain.find("login", "user"), Key("enter")]})
