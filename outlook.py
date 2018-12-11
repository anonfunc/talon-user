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


ctx = Context("outlook", bundle="com.microsoft.Outlook")
ctx.keymap(
    {
        "archive": Key("ctrl+e")
    }
)
