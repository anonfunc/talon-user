import talon.clip as clip
from talon.voice import Context, Key, press
from user.utility import text, parse_words, join_words

supported_apps = {
    "com.jetbrains.intellij",
    "com.jetbrains.intellij.ce",
    "com.jetbrains.AppCode",
    "com.jetbrains.CLion",
    "com.jetbrains.datagrip",
    "com.jetbrains.goland",
    "com.jetbrains.PhpStorm",
    "com.jetbrains.pycharm",
    "com.jetbrains.rider",
    "com.jetbrains.rubymine",
    "com.jetbrains.WebStorm",
    "com.google.android.studio",
    "com.microsoft.VSCode",
}


ctx = Context(
    "notsupported", func=lambda app, _: not any(app.bundle == b for b in supported_apps)
)


# jcooper-korg from talon slack
def select_text_to_left_of_cursor(m):
    words = parse_words(m)
    if not words:
        return
    old = clip.get()
    key = join_words(words).lower()
    press("shift-home", wait=2000)
    press("cmd-c", wait=2000)
    press("right", wait=2000)
    text_left = clip.get()
    clip.set(old)
    result = text_left.find(key)
    if result == -1:
        return
    # cursor over to the found key text
    for i in range(0, len(text_left) - result):
        press("left", wait=0)
    # now select the matching key text
    for i in range(0, len(key)):
        press("shift-right")


# jcooper-korg from talon slack
def select_text_to_right_of_cursor(m):
    words = parse_words(m)
    if not words:
        return
    key = join_words(words).lower()
    old = clip.get()
    press("shift-end", wait=2000)
    press("cmd-c", wait=2000)
    press("left", wait=2000)
    text_right = clip.get()
    clip.set(old)
    result = text_right.find(key)
    if result == -1:
        return
    # cursor over to the found key text
    for i in range(0, result):
        press("right", wait=0)
    # now select the matching key text
    for i in range(0, len(key)):
        press("shift-right")


keymap = {}
keymap.update(
    {
        "(select previous | trail) [<dgndictation>]": select_text_to_left_of_cursor,
        "(select next | crew) [<dgndictation>]": select_text_to_right_of_cursor,
        "search [<dgndictation>]": [Key("cmd-f"), text],
        "select [this] line": [Key("cmd-left"), Key("shift-end")],
        "(clean | clear) line": [Key("cmd-left"), Key("shift-end"), Key("delete")],
        "delete line": [
            Key("cmd-left"),
            Key("shift-end"),
            Key("delete"),
            Key("delete"),
        ],
        "delete to end": [Key("shift-end"), Key("delete")],
        "delete to start": [Key("shift-home"), Key("delete")],
    }
)

ctx.keymap(keymap)
