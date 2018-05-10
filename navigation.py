from talon.voice import Context, Key

ctx = Context("navigation")


keymap = {
    # Application navigation
    "launcher": Key("cmd-space"),
    "swick": Key("cmd-tab"),
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
    "trough": Key("alt-backspace"),
    # moving
    "(tab | tarp)": Key("tab"),
    "tarsh": Key("shift-tab"),
    "slap": [Key("cmd-right enter")],
    # 'shocker': [Key('cmd-left enter up')],
    # 'wonkrim': Key('alt-ctrl-left'),
    # 'wonkrish': Key('alt-ctrl-right'),
    "fame": Key("alt-left"),
    # 'locky soup': [Key('alt-left'),Key('alt-left')],
    # 'locky trace': [Key('alt-left'),Key('alt-left'),Key('alt-left')],
    "fish": Key("alt-right"),
    "ricky": Key("cmd-right"),
    "lefty": Key("cmd-left"),
    "(left | crimp)": Key("left"),
    "(right | chris)": Key("right"),
    "jeep": Key("up"),
    "(down | dune | doom)": Key("down"),
    # selecting
    "snatch": Key("cmd-x"),
    "stoosh": Key("cmd-c"),
    "spark": Key("cmd-v"),
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
