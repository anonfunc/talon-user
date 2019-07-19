from talon import ctrl
from talon.voice import Context, Key

from ..utils import numerals, text_to_number, delay

ctx = Context("amethyst")


def mod1(key):
    return Key("alt+shift+" + key)


def mod2(key):
    def do_it(_):
        ctrl.key_press(key, shift=True, ctrl=True, alt=True)

    return do_it


def number(control=False, mod_one=False):
    def do_it(m):
        # noinspection PyProtectedMember
        num = text_to_number(m._words[-1])
        if num < 10:
            ctrl.key_press(str(num), ctrl=control, alt=mod_one, shift=mod_one)

    return do_it


ctx.keymap(
    {
        "next layout": mod1("space"),
        "last layout": mod2("down"),  # REBIND in AMETHYST
        "focus (first | left)": mod1("w"),
        "move [to] (first | left)": mod2("w"),
        "send [to] left": [mod2("w"), delay(0.3), mod1("e")],
        "swap [with] left": [mod2("w"), delay(0.3), mod1("j"), delay(0.3), mod2("e")],
        "take from (first | left)": [mod1("w"), delay(0.3), mod2("e")],
        "focus (second | middle)": mod1("e"),
        "(move | send) [to] (second | middle)": mod2("e"),
        # "send [to] second": [mod2("e"), mod1("e")],
        "focus right": mod1("r"),
        "move [to] right": mod2("r"),
        "send [to] right": [mod2("r"), delay(0.3), mod1("e")],
        "take from right": [mod1("r"), delay(0.3), mod2("e")],
        "swap [with] right": [mod2("r"), delay(0.3), mod1("j"), delay(0.3), mod2("e")],
        # "third focus": mod1("r")
        # "third move": mod2("r")
        "shrink pane": mod1("h"),
        "grow pane": mod1("l"),
        "more windows": mod1(","),
        "fewer windows": mod1("."),
        "focus (last slot | counter clockwise)": mod1("j"),
        "move (last slot |  counter clockwise)": mod2("j"),
        "focus (next slot | clockwise)": mod1("k"),
        "move (next slot | clockwise)": mod2("k"),
        # "move (next | clockwise) space": mod2("h"),
        # "move (last | previous | counter clockwise) space": mod2("l"),
        "move [to] main": mod1("return"),
        "toggle (float | floating)": mod1("t"),
        "toggle (amethyst | tiling)": mod2("t"),
        "show (layouts | layout)": mod1("i"),
        "tall layout": mod1("a"),
        "wide layout": mod1("s"),
        "fix layout": mod1("z"),
        "(full | full screen) layout": mod1("d"),
        "(call on | column) layout": mod1("f"),
        # "binary layout": mod1("g"),
        f"move to next space": mod2("right"),
        f"move to last space": mod2("left"),
        # Needs space shortcuts
        f"move to [space] {numerals}": [number(mod_one=True, control=True), number(control=True)],
        f"send to [space] {numerals}": number(mod_one=True, control=True),
        # Not strictly Amethyst
        f"focus [space] {numerals}": number(control=True),
        "mission control": Key("ctrl-up"),
        "(app | application) windows": Key("ctrl-down"),
        f"focus next space": Key("ctrl-right"),
        f"focus last space": Key("ctrl-left"),
    }
)
