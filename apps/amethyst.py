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
        ###
        # Spaces!
        ###
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

        ###
        # Top / Bottom Screens, Bottom Main
        ###
        "focus [the] (first | bottom)": mod1("w"),
        "send [to] (first | bottom)": [mod2("w"), delay(0.3), mod1("e")],
        "move [to] (first | bottom)": mod2("w"),
        "swap [with] (first | bottom)": [mod2("w"), delay(0.3), mod1("j"), delay(0.3), mod2("e")],
        "take [from] (first | bottom)": [mod1("w"), delay(0.3), mod2("e")],
        
        "focus [the] (second | top)": mod1("e"),
        "send [to] (second | top)": [mod2("e"), delay(0.3), mod1("w")],
        "move [to] (second | top)": mod2("e"),
        "swap [with] (second | top)": [mod2("e"), delay(0.3), mod1("j"), delay(0.3), mod2("e")],
        "take [from] (second | top)": [mod1("e"), delay(0.3), mod2("w")],
        
        ###
        # Left / Middle / Right, Middle Main
        ###
        # "focus [the] (first | left)": mod1("w"),
        # "send [to] (first | left)": [mod2("w"), delay(0.3), mod1("e")],
        # "move [to] (first | left)": mod2("w"),
        # "swap [with] (first | left)": [mod2("w"), delay(0.3), mod1("j"), delay(0.3), mod2("e")],
        # "take [from] (first | left)": [mod1("w"), delay(0.3), mod2("e")],
        
        # "focus [the] (second | middle)": mod1("e"),
        # "send [to] (second | middle)": [mod2("e"), delay(0.3), mod1("w")],
        # "move [to] (second | middle)": mod2("e"),
        # "swap [with] (second | middle)": [mod2("e"), delay(0.3), mod1("j"), delay(0.3), mod2("e")],
        # "take [from] (second | middle)": [mod1("e"), delay(0.3), mod2("w")],

        # "focus [the] (third | right)": mod1("r"),
        # "send [to] (third | right)": [mod2("r"), delay(0.3), mod1("e")],
        # "move [to] (third | right)": mod2("r"),
        # "swap [with] (third | right)": [mod2("r"), delay(0.3), mod1("j"), delay(0.3), mod2("e")],
        # "take [from] (third | right)": [mod1("r"), delay(0.3), mod2("e")],
        
        ###
        # Pane / Window Commands
        # Calling the managed "windows" slots to distinguish from Cmd-` as "next window of app"
        ###
        "shrink slot": mod1("h"),
        "grow slot": mod1("l"),
        
        "more slots": mod1(","),
        "fewer slots": mod1("."),
        "[focus] last slot": mod1("j"),
        "move [to] last slot": mod2("j"),
        "[focus] next slot": mod1("k"),
        "move [to] next slot": mod2("k"),
        # Not binding these...
        # "move (next | clockwise) space": mod2("h"),
        # "move (last | previous | counter clockwise) space": mod2("l"),
        "move [to] main slot": mod1("return"),

        ###
        # Layout commands
        ###
        "toggle (float | floating)": mod1("t"),
        "toggle (amethyst | tiling)": mod2("t"),
        "next layout": mod1("space"),
        "last layout": mod2("down"),  # REBIND in AMETHYST
        "show (layouts | layout)": mod1("i"),
        "tall layout": mod1("a"),
        "wide layout": mod1("s"),
        "fix layout": mod1("z"),
        "(full | full screen) layout": mod1("d"),
        "(call on | column) layout": mod1("f"),
        # "binary layout": mod1("g"),
    }
)
