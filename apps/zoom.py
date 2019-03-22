from talon.voice import Context, ContextGroup, Key
from talon_plugins import speech

from ..utils import text

dictation_group = ContextGroup("zoom")
ctx = Context("zoom", bundle="us.zoom.xos", group=dictation_group)
ctx.keymap(
    {
        "toggle Mike": [Key("cmd-shift-a"), lambda m: speech.set_enabled(False)],
        "toggle video": [Key("cmd-shift-v")],
    }
)
dictation_group.load()
