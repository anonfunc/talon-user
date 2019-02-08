import time

from talon.voice import Context, ContextGroup, Key

from ..utils import text


def delay(amount):
    return lambda _: time.sleep(amount)


# I don't want to interleave jira navigation with other commands, like dictation.
group = ContextGroup("jira")

browsers = {"Google Chrome", "Firefox", "Safari"}

def isJira(app, win):
    return app.name in browsers and " JIRA2" in win.title


ctx = Context("jira", func=isJira, group=group)
ctx.vocab = ["sub-task", "Dwight"]
ctx.keymap(
    {
        "dashboard": Key("g d"),
        "boards": Key("g b"),
        "issues": Key("g i"),
        "find": Key("/"),
        "create": Key("c"),
        "assign [to] <dgndictation> [over]": [Key("a"), delay(0.6), text],
        "assign to me": Key("i"),
        "comment": Key("m"),
        "edit": Key("e"),
        "action <dgndictation> [over]": [Key("."), delay(0.6), text],
        "submit": Key("ctrl+return"),
        "copy link": Key("cmd+l cmd+c"),
        "copy id": Key("cmd+l right alt+shift+left alt+shift+left cmd+c"),
    }
)
group.load()
