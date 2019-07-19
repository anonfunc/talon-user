import subprocess
import time

from talon import keychain
import talon.clip as clip
from talon.voice import Context, Key, press

from ..utils import text, select_last_insert, delay, add_vocab


def learn_selection(_):
    with clip.capture() as s:
        press("cmd-c", wait=2000)
    words = s.get().split()
    add_vocab(words)


ctx = Context("misc")
ctx.vocab = ["Jira"]
ctx.keymap(
    {
        "learn selection": learn_selection,
        "(alfred | launch)": Key("cmd-space"),
        "(alfred | launch) <dgndictation> [over]": [Key("cmd-space"), delay(0.4), text],
        "correct": select_last_insert,
        "toggle dark": lambda _: subprocess.check_call(
            ["open", "/System/Library/CoreServices/ScreenSaverEngine.app"]
        ),
        "go toolbox": Key("cmd+shift+ctrl+f1"),
        "password amigo": keychain.find("login", "user"),
        "snippet [<dgndictation>]": [  # XXX Doesn't really go here
            Key("cmd-shift-j"),
            delay(0.1),
            text,
        ],
        "under": delay(0.2),
        # Clipboard
        "clippings [<dgndictation>]": [Key("cmd+ctrl+c"), delay(0.1), text],
        "(kapeli | Cappelli)": Key("cmd-shift-space"),
        # Menubar:
        "menubar": Key("ctrl-f2"),
        "menubar <dgndictation> [over]": [Key("cmd+shift+/"), delay(0.1), text],
        "menu icons": Key("ctrl-f8"),
        # Bartender needed for this one
        "menu search": Key("ctrl-shift-f8"),
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
