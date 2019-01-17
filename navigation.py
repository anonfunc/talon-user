import time

from talon.voice import Context, Key

from .utility import text

ctx = Context("navigation")

ctx.keymap(
    {
        # Application navigation
        # XXX delay is janky, wait until alfred focuses?
        "launcher [<dgndictation>]": [
            Key("cmd-space"),
            lambda _: time.sleep(0.4),
            text,
        ],
        "delete [last] word": Key("alt-backspace"),
        "delete next word": Key("alt-delete"),
        # moving
        "(tab | tarp | indent)": Key("tab"),
        "(dedent | didn't | tarsh)": Key("shift-tab"),
        "slap": [Key("cmd-right enter")],
        # 'shocker': [Key('cmd-left enter up')],
        "(leftward | left word)": Key("alt-left"),
        "(rightward | right word)": Key("alt-right"),
        # selecting
        "cut this": Key("cmd-x"),
        "copy this": Key("cmd-c"),
        "paste here": Key("cmd-v"),
        "select up": Key("shift-up"),
        "select down": Key("shift-down"),
    }
)
