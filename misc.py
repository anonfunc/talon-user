import subprocess

import time
from talon.voice import Context, Key
from user.utility import text

ctx = Context("misc")

ctx.keymap({
})

ctx = Context("shortcat")

ctx.keymap({
    "(shortcat | short cap | shortcut) [<dgndictation>]": [Key("cmd+shift+ctrl+f14"), text],
})