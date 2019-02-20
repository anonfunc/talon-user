import subprocess
import time

from talon import keychain
from talon.voice import Context, Key

from ..utils import text

ctx = Context("misc")
ctx.vocab = ["Jira"]
ctx.keymap(
    {
        "launch [<dgndictation>]": [Key("cmd-space"), lambda _: time.sleep(0.4), text],
        "go dark": lambda _: subprocess.check_call(
            ["open", "/System/Library/CoreServices/ScreenSaverEngine.app"]
        ),
        "go toolbox": Key("cmd+shift+ctrl+f1"),
        "password amigo": keychain.find("login", "user"),
        "snippet [<dgndictation>]": [  # XXX Doesn't really go here
            Key("cmd-shift-j"),
            lambda _: time.sleep(0.1),
            text,
        ],
        # Clipboard
        "clippings [<dgndictation>]": [
            Key("cmd+ctrl+c"),
            lambda _: time.sleep(0.1),
            text,
        ],
        "cut this": Key("cmd-x"),
        "copy this": Key("cmd-c"),
        "paste": Key("cmd-v"),
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
