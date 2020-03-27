from talon.ui import active_app
from talon.voice import Context, Key

from ..utils import delay, text

enabled = False


def is_firefox(app, _):
    global enabled
    return enabled and app.name == "Firefox"


# Assuming that https://addons.mozilla.org/en-US/firefox/addon/modeless-keyboard-navigation/
# is installed:
#
# <c-,> open a link in the current tab
# <c-.> open a link in a new tab
# <a-f> open multiple links in new tabs
# <c-[> cycle forward to the next frame
# <c-;> open bookmark
# <c-'> open bookmark in a new tab
#
# Assuming https://addons.mozilla.org/en-US/firefox/addon/detach-tab/?src=search
# Default keyboard shortcut for detaching tab is Ctrl+Shift+Space.
# You should change it to MacCtrl+Shift+Space, as the other is really Command-Shift-Space.
#
# Assuming https://addons.mozilla.org/en-US/firefox/addon/tab_search/?src=search
# Ctrl + Shift + F - Toggle extension (Windows/Linux)
# Cmd + Shift + L - Toggle extension (macOS)
# Ctrl + Backspace - Delete tab
# Enter - Open selected tab or first in list if not selected
# Up/Left - Select previous tab
# Down/Right - Select next tab
# Alt + R - Refresh tab
# Alt + P - Pin tab
# Ctrl + C - Copy Tab URL
# Alt + Shift + D - Delete all duplicate tabs
# Alt + M - Mute (only if tab is audible)
#
#

ctx = Context("firefox", func=is_firefox)
ctx.keymap(
    {
        "(follow | go link)": Key("ctrl-,"),
        "go tab": Key("ctrl-."),
        "go back": Key("cmd-["),
        "go forward": Key("cmd-]"),
        "clear tab": Key("cmd-w"),
        "restore tab": Key("cmd-shift-t"),
        "jump [<dgndictation>] [over]": [
            Key("cmd-shift-l"),
            delay(0.2),
            text,
        ],
        "tab search [<dgndictation>] [over]": [Key("cmd-shift-l"), delay(0.2), text],
        # "open here [<dgndictation>] [over]": [Key("o"), delay(0.1), text],
        # "open tab [<dgndictation>] [over]": [Key("t"), delay(0.1), text],
        "search": Key("cmd-f"),
        "search [<dgndictation>] [over]": [Key("cmd-f"), delay(0.1), text],
        "go next tab": Key("cmd-shift-]"),
        "go last tab": Key("cmd-shift-["),
        "toggle mark": Key("cmd-d"),
        "toggle reader": Key("cmd-alt-r"),
        "mark pin board": Key("alt-p"),
        "copy (URL | location)": [Key("cmd-l cmd-c")],
        # "go next page": Key("]]"),
        # "go last page": Key("[["),
        "zoom out": Key("cmd-="),
        "zoom in": Key("cmd--"),
        "zoom clear": Key("cmd-0"),
        "detach tab": Key("ctrl-shift-space"),
    }
)
