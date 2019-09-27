import subprocess

import talon.clip as clip
from talon.voice import Context, Key, press

from talon import applescript, keychain, tap, ui
from talon_plugins import microphone
from ..utils import add_vocab, delay, select_last_insert, text


def learn_selection(_):
    with clip.capture() as s:
        press("cmd-c", wait=2000)
    words = s.get().split()
    add_vocab(words)
    print("Learned " + ",".join(words))


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
        "terminal": lambda _: [ui.launch(bundle="com.googlecode.iterm2")],
        # "focus GoLand": lambda _: [ui.launch(bundle="com.jetbrains.goland")],
        # "focus PyCharm": lambda _: [ui.launch(bundle="com.jetbrains.pycharm")],
        "go toolbox": Key("cmd+shift+ctrl+f1"),
        "password amigo": keychain.find("login", "user"),
        "snippet [<dgndictation>]": [  # XXX Doesn't really go here
            Key("cmd-shift-j"),
            delay(0.1),
            text,
        ],
        # "under": delay(0.2),
        # Clipboard
        "clippings [<dgndictation>]": [Key("cmd+ctrl+c"), delay(0.1), text],
        "(kapeli | Cappelli)": Key("cmd-shift-space"),
        # Menubar:
        "menubar": Key("ctrl-f2"),
        "menubar <dgndictation> [over]": [Key("cmd+shift+/"), delay(0.1), text],
        "menu icons": Key("ctrl-f8"),
        # Bartender needed for this one
        "menu search": Key("ctrl-shift-f8"),
        # Different input volume levels
        "input volume high": lambda _: applescript.run("set volume input volume 90"),
        "input volume low": lambda _: applescript.run("set volume input volume 50"),
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


def screensaver_hotkey(_, e):
    # print(e)
    if e == "cmd-ctrl-§" and e.down:
        subprocess.check_call(
            ["open", "/System/Library/CoreServices/ScreenSaverEngine.app"]
        ),
        e.block()
    return True


tap.register(tap.HOOK | tap.KEY, screensaver_hotkey)


# Default to krisp on startup, if present.
def _use_krisp():
    # noinspection PyUnresolvedReferences
    mics = {i.name: i for i in list(microphone.manager.menu.items)}
    krisp = "krisp microphone"
    if krisp in mics:
        microphone.manager.menu_click(mics[krisp])


_use_krisp()
