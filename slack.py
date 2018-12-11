import os
import re
import subprocess
import time

from talon import applescript
import talon.clip as clip
from talon.api import ffi
from talon.voice import Key, press, Str, Context

from user.utility import text

from user.mouse import delayed_click


ctx = Context("slack", bundle="com.tinyspeck.slackmacgap")
ctx.keymap(
    {
        "jump": Key("cmd-k"),
        "(dm's | direct messages | messages)": Key("cmd-shift-k"),
        "(and read | unread)": Key("cmd-shift-a"),
        "(threads | all threads)": Key("cmd-shift-t"),
        "react [<dgndictation>]": [Key("cmd-shift-\\"), text],
        "zoom": Key("cmd-."),
        "next unread": Key("alt-shift-down"),
    }
)
