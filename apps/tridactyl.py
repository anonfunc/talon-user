import time

from talon.ui import active_app
from talon.voice import Context, Key


def delay(amount):
    return lambda _: time.sleep(amount)


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
        "go next tab": "gt",
        "go last tab": "gT",
        "search": "/",
        "toggle mark": "A",
        "toggle reader": "gr",
        "copy URL": "yy",
        "go next page": "]]",
        "go last page": "[[",
        "go edit": Key("ctrl-i"),
    }
)
