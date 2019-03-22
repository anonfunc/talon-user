import time

from talon.voice import Context, ContextGroup, Key

from .tridactyl import tKey
from ..utils import text, delay

# I don't want to interleave jira navigation with other commands, like dictation.
group = ContextGroup("jira")

browsers = {"Google Chrome", "Firefox", "Safari"}


def isJira(app, win):
    return app.name in browsers and " JIRA2" in win.title


ctx = Context("jira", func=isJira, group=group)
ctx.vocab = ["sub-task", "Dwight"]
ctx.keymap(
    {
        "go dashboard": tKey("g d"),
        "go boards": tKey("g a"),
        "go issues": tKey("g i"),
        "search": tKey("/"),
        "go create": tKey("c"),
        "assign [to] <dgndictation> [over]": [tKey("a"), delay(0.6), text],
        "assign to me": tKey("i"),
        "comment": tKey("m"),
        "edit": tKey("e"),
        "(action | please) [<dgndictation>] [over]": [tKey("."), delay(0.6), text],
        "submit": tKey("ctrl+return"),
        "copy link": tKey("cmd+l cmd+c"),
        "copy id": tKey("cmd+l right alt+shift+left alt+shift+left cmd+c"),
    }
)
group.load()
