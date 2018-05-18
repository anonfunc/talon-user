import time
from talon.voice import Context, Key
from user.utility import text

ctx = Context("navigation")

keymap = {
    # Application navigation
    # XXX delay is janky, wait until alfred focuses?
    "launcher [<dgndictation>]": [Key("cmd-space"), lambda _: time.sleep(0.4), text],
    "tab close": Key("cmd-w"),
    "window new": Key("cmd-n"),
    "(window next | gibby)": Key("cmd-`"),
    "(window last | shibby)": Key("cmd-shift-`"),
    "window space right": Key("cmd-alt-ctrl-right"),
    "window space left": Key("cmd-alt-ctrl-left"),
    # Following commands should be application specific
    "freshly": Key("cmd-r"),
    "baxley": Key("cmd-left"),
    # deleting
    "kite": Key("alt-delete"),
    "snip left": Key("cmd-shift-left delete"),
    "snip right": Key("cmd-shift-right delete"),
    "slurp": Key("backspace delete"),
    "delete [last] word": Key("alt-backspace"),
    "delete next word": Key("alt-delete"),
    # moving
    "(tab | tarp | indent)": Key("tab"),
    "(dedent | didn't | tarsh)": Key("shift-tab"),
    "slap": [Key("cmd-right enter")],
    # 'shocker': [Key('cmd-left enter up')],
    # 'wonkrim': Key('alt-ctrl-left'),
    # 'wonkrish': Key('alt-ctrl-right'),
    "(leftward | left word)": Key("alt-left"),
    # 'locky soup': [Key('alt-left'),Key('alt-left')],
    # 'locky trace': [Key('alt-left'),Key('alt-left'),Key('alt-left')],
    "(rightward | right word)": Key("alt-right"),
    "ricky": Key("cmd-right"),
    "lefty": Key("cmd-left"),
    "(left | crimp)": Key("left"),
    "(right | chris)": Key("right"),
    "jeep": Key("up"),
    "(down | dune | doom)": Key("down"),
    # selecting
    "(snatch | cut this)": Key("cmd-x"),
    "(stoosh | copy this)": Key("cmd-c"),
    "(spark | paste here)": Key("cmd-v"),
    "shreepway": Key("cmd-shift-up"),
    "shroomway": Key("cmd-shift-down"),
    "shreep": Key("shift-up"),
    "shroom": Key("shift-down"),
    "lecksy": Key("cmd-shift-left"),
    "ricksy": Key("cmd-shift-right"),
    "shlocky": Key("alt-shift-left"),
    "shrocky": Key("alt-shift-right"),
    "shlicky": Key("shift-left"),
    "shricky": Key("shift-right"),
}
ctx.keymap(keymap)
