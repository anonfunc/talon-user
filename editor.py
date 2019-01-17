import talon.clip as clip
from talon.voice import Context, Key, press

from .ext.homophones import homophone_lookup
from .utility import join_words, parse_words, text

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
    key = join_words(words).lower()
    keys = homophone_lookup.get(key, [key])
    press("left", wait=2000)
    press("right", wait=2000)
    press("shift-home", wait=2000)
    with clip.capture() as s:
        press("cmd-c", wait=2000)
    press("right", wait=2000)
    text_left = s.get()
    result = -1
    for needle in keys:
        result = max(text_left.find(needle), result)
    print(text_left, keys, result)
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
    keys = homophone_lookup.get(key, [key])
    press("right", wait=2000)
    press("left", wait=2000)
    press("shift-end", wait=2000)
    with clip.capture() as s:
        press("cmd-c", wait=2000)
    text_right = s.get()
    press("left", wait=2000)
    result = len(text_right) + 1
    for needle in keys:
        index = text_right.find(needle)
        if index == -1:
            continue
        result = min(index, result)
    print(text_right, keys, result, len(text_right) + 1)
    if result == len(text_right) + 1:
        return
    # cursor over to the found key text
    for i in range(0, result):
        press("right", wait=0)
    # now select the matching key text
    for i in range(0, len(key)):
        press("shift-right")


ctx.keymap(
    {
        "(select previous) [<dgndictation>]": select_text_to_left_of_cursor,
        "(select next) [<dgndictation>]": select_text_to_right_of_cursor,
        "search [<dgndictation>]": [Key("cmd-f"), text],
        "select all": [Key("cmd-a")],
        "select [this] line": [Key("home"), Key("shift-end")],
        "(clean | clear) line": [Key("home"), Key("shift-end"), Key("delete")],
        "delete line": [Key("home"), Key("shift-end"), Key("delete"), Key("delete")],
        "delete to end": [Key("shift-end"), Key("delete")],
        "delete to start": [Key("shift-home"), Key("delete")],
    }
)
