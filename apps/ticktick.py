from talon import ctrl
from talon.voice import Context, Key

from ..utils import text, delay

ctx = Context("1password")
ctx.keymap({
    "password [<dgndictation>] [over]": [Key("shift-cmd-\\"), delay(0.2), text],
})