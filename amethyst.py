import subprocess

import time
from talon import ctrl
from talon.voice import Context, Key
from user.utility import text, text_to_number, numerals

ctx = Context("amethyst")


def mod1(key):
    return Key("alt+shift+"+key)


def mod2(key):
    def do_it(m):
        ctrl.key_press(key, shift=True, ctrl=True, alt=True)
    return do_it


def number(control=False, mod1=False):
    def do_it(m):
        num = text_to_number(m._words[-1])
        if num<10:
            ctrl.key_press(str(num), ctrl=control, alt=mod1, shift=mod1)
    return do_it

ctx.keymap({
    "next layout": mod1("space"),
    "(last | previous) layout": mod2("down"),  # REBIND in AMETHYST
    "focus first": mod1("w"),
    "move [to] first": mod2("w"),
    "send [to] first": [mod2("w"), mod1("w")],
    "focus second": mod1("e"),
    "move [to] second": mod2("e"),
    "send [to] second": [mod2("e"), mod1("e")],
    # "third focus": mod1("r")
    # "third move": mod2("r")
    "shrink pane": mod1("h"),
    "grow pane": mod1("l"),
    "(more | increase) windows": mod1(","),
    "(fewer | decrease) windows": mod1("."),
    "focus (last | previous | counter clockwise)": mod1("j"),
    "move (last | previous | counter clockwise)": mod2("j"),
    "focus (next | clockwise)": mod1("k"),
    "move (next | clockwise)": mod2("k"),
    # "move (next | clockwise) space": mod2("h"),
    # "move (last | previous | counter clockwise) space": mod2("l"),
    "move [to] main": mod1("return"),
    "toggle (float | floating)": mod1("t"),
    "toggle (amethyst | tiling)": mod2("t"),
    "show layouts": mod1("i"),
    "tall layout": mod1("a"),
    "wide layout": mod1("s"),
    "(full | full screen) layout": mod1("d"),
    "(call on | column) layout": mod1("f"),
    f"move [to] next space": mod2("right"),
    f"move [to] (previous | last) space": mod2("left"),

    ## Needs space shortcuts
    f"move [to] space {numerals}": number(mod1=True, control=True),
    ## Not strictly Amethyst
    f"focus space {numerals}": number(control=True),
    "mission control": Key("ctrl-up"),
    "(app | application) windows": Key("ctrl-down"),
    f"focus [to] next space": Key("ctrl-right"),
    f"focus [to] (previous | last) space": Key("ctrl-left"),
})