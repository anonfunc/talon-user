import subprocess

import time
from talon.voice import Context, Key
from user.utility import text

ctx = Context("navigation")

keymap = {
    # Application navigation
    # XXX delay is janky, wait until alfred focuses?
    "launcher [<dgndictation>]": [Key("cmd-space"), lambda _: time.sleep(0.4), text],
    "mission control": Key("ctrl-up"),
    "tab close": Key("cmd-w"),
    "window new": Key("cmd-n"),
    "window next": Key("cmd-`"),
    "window last": Key("cmd-shift-`"),
    "window space right": Key("cmd-alt-ctrl-right"),
    "window space left": Key("cmd-alt-ctrl-left"),
    # Following commands should be application specific
    "freshly": Key("cmd-r"),
    "baxley": Key("cmd-left"),
    # deleting
    # "kite": Key("alt-delete"),
    # "snip left": Key("cmd-shift-left delete"),
    # "snip right": Key("cmd-shift-right delete"),
    #"slurp": Key("backspace delete"),
    "delete [last] word": Key("alt-backspace"),
    "delete next word": Key("alt-delete"),
    # moving
    "(tab | tarp | indent)": Key("tab"),
    "(dedent | didn't | tarsh)": Key("shift-tab"),
    "slap": [Key("cmd-right enter")],
    # 'shocker': [Key('cmd-left enter up')],
    "(leftward | left word)": Key("alt-left"),
    "(rightward | right word)": Key("alt-right"),
    # "righty": Key("cmd-right"),
    # "lefty": Key("cmd-left"),
    # "left": Key("left"),
    # "right": Key("right"),
    # "jeep": Key("up"),
    # selecting
    "cut this": Key("cmd-x"),
    "copy this": Key("cmd-c"),
    "paste here": Key("cmd-v"),
    "select up": Key("shift-up"),
    "select down": Key("shift-down"),
}
ctx.keymap(keymap)
