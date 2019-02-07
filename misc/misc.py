import subprocess
import time

from talon import keychain
from talon.voice import Context, Key

from ..utils import text

ctx = Context("misc")
ctx.vocab = [
    "Jira"
]
ctx.keymap(
    {
        "go dark": lambda _: subprocess.check_call(
            ["open", "/System/Library/CoreServices/ScreenSaverEngine.app"]
        ),
        "toolbox": Key("cmd+shift+ctrl+f1"),
        "password amigo": keychain.find("login", "user"),
        "snippet [<dgndictation>]": [  # XXX Doesn't really go here
            Key("cmd-shift-j"),
            lambda _: time.sleep(0.1),
            text,
        ],
        "clippings [<dgndictation>]": [Key("cmd+ctrl+c"), lambda _: time.sleep(0.1), text],
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
ctx.keymap(
    {
        "amigo": [keychain.find("login", "user"), Key("enter")],
    }
)
