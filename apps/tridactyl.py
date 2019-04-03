from talon.ui import active_app
from talon.voice import Context, Key

from ..utils import delay, text
enabled = True


def is_tridactyl(app, _):
    global enabled
    return enabled and app.name == "Firefox"


# noinspection PyPep8Naming
def tKey(key):
    """Key(), but for conflicts with Tridactyl commands"""
    global enabled

    def tKeyM(m):
        if is_tridactyl(active_app(), None):
            return Key("shift-escape " + key + " shift-escape")(m)
        else:
            return Key(key)(m)

    return tKeyM


ctx = Context("firefox", func=is_tridactyl)
ctx.keymap(
    {
        "(follow | go link)": "f",
        "go background": "F",
        "go back": "H",
        "go forward": "L",
        "clear tab": "d",
        "restore tab": "u",
        "jump [<dgndictation>] [over]": ["B", delay(0.1), text],  # Alltabs is more useful
        "open [<dgndictation>] [over]": ["o", delay(0.1), text],
        "create tab [<dgndictation>] [over]": ["t", delay(0.1), text],
        "search [<dgndictation>] [over]": ["s", delay(0.1), text],
        "tab search [<dgndictation>] [over]": ["S", delay(0.1), text],
        "go next tab": "gt",
        "go last tab": "gT",
        "search": "/",
        "toggle mark": "A",
        "toggle ignore": Key("shift-escape"),
        "toggle reader": "gr",
        "copy URL": "yy",
        "go next page": "]]",
        "go last page": "[[",
        "zoom out": "zo",
        "zoom in": "zi",
        "zoom clear": "zz",
        "go edit": Key("ctrl-i"),
        "detach tab": [":", delay(0.1), "tabdetach", delay(0.1), "\n"],
    }
)
