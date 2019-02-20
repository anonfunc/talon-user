import talon.clip as clip
from talon.voice import Context, Key, press

from .. import utils
from ..apps.jetbrains import port_mapping

try:
    from ..text.homophones import all_homophones

    # Map from every homophone back to the row it was in.
    homophone_lookup = {
        item.lower(): words for canon, words in all_homophones.items() for item in words
    }
except ImportError:
    homophone_lookup = {"right": ["right", "write"], "write": ["right", "write"]}
    all_homophones = homophone_lookup.keys()

extension = None


def extendable(d):
    def wrapper(m):
        global extension
        extension = Key(d)
        extension(m)

    return wrapper


def set_extension(d):
    def wrapper(_):
        global extension
        extension = d

    return wrapper


supported_apps = {"com.microsoft.VSCode"}
supported_apps.update(port_mapping.keys())


def not_supported_editor(app, window):
    if str(app.bundle) in supported_apps:
        return False
    return True


ctx = Context(
    "notsupported", func=not_supported_editor
)


# jcooper-korg from talon slack
def select_text_to_left_of_cursor(m):
    words = utils.parse_words(m)
    if not words:
        return
    key = utils.join_words(words).lower()
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
        find = text_left.find(needle)
        if find > result:
            result = find
            key = needle
            break

    # print(text_left, keys, result)
    if result == -1:
        return
    # cursor over to the found key text
    for i in range(0, len(text_left) - result):
        press("left", wait=0)
    # now select the matching key text
    for i in range(0, len(key)):
        press("shift-right")
    set_extension(lambda _: select_text_to_left_of_cursor(m))


# jcooper-korg from talon slack
def select_text_to_right_of_cursor(m):
    words = utils.parse_words(m)
    if not words:
        return
    key = utils.join_words(words).lower()
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
        if index < result:
            result = index
            key = needle
            break

    # print(text_right, keys, result, len(text_right) + 1)
    if result == len(text_right) + 1:
        return
    # cursor over to the found key text
    for i in range(0, result):
        press("right", wait=0)
    # now select the matching key text
    for i in range(0, len(key)):
        press("shift-right")
    set_extension(lambda _: select_text_to_right_of_cursor(m))


ctx.keymap(
    {
        # moving
        # left, right, up and down already defined
        "go word left": extendable("alt-left"),
        "go word right": extendable("alt-right"),
        "go line start": extendable("cmd-left"),
        "go line end": extendable("cmd-right"),
        "go way left": extendable("cmd-left"),
        "go way right": extendable("cmd-right"),
        "go way down": extendable("cmd-down"),
        "go way up": extendable("cmd-up"),
        # selecting
        "select all": [Key("cmd-a")],
        "select last <dgndictation>": select_text_to_left_of_cursor,
        "select next <dgndictation>": select_text_to_right_of_cursor,
        "select line": extendable("cmd-left cmd-left cmd-shift-right"),
        "select left": extendable("shift-left"),
        "select right": extendable("shift-right"),
        "select up": extendable("shift-up"),
        "select down": extendable("shift-down"),
        "select word left": [
            Key("left shift-right left alt-left alt-right shift-alt-left"),
            set_extension(Key("shift-alt-left")),
        ],
        "select word right": [
            Key("right shift-left right alt-right alt-left shift-alt-right"),
            set_extension(Key("shift-alt-right")),
        ],
        "extend": extension,
        "select way left": extendable("cmd-shift-left"),
        "select way right": extendable("cmd-shift-right"),
        "select way up": extendable("cmd-shift-up"),
        "select way down": extendable("cmd-shift-down"),
        # deleting
        "clear line": extendable("cmd-left cmd-left cmd-shift-right delete cmd-right"),
        "clear left": extendable("backspace"),
        "clear right": extendable("delete"),
        "clear up": extendable("shift-up delete"),
        "clear down": extendable("shift-down delete"),
        "clear word left": extendable("alt-backspace"),
        "clear word right": extendable("alt-delete"),
        "clear way left": extendable("cmd-shift-left delete"),
        "clear way right": extendable("cmd-shift-right delete"),
        "clear way up": extendable("cmd-shift-up delete"),
        "clear way down": extendable("cmd-shift-down delete"),
        # searching
        "search [<dgndictation>]": [Key("cmd-f"), utils.text],
    }
)