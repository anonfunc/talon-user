import re

import talon.clip as clip
from talon.voice import Context, Key, press

from .. import utils
from ..apps.jetbrains import port_mapping
from ..text.homophones import raise_homophones
from ..misc.basic_keys import alphabet

try:
    from ..text.homophones import all_homophones

    # Map from every homophone back to the row it was in.
    homophone_lookup = {
        item.lower(): words for canon, words in all_homophones.items() for item in words
    }
except ImportError:
    homophone_lookup = {"right": ["right", "write"], "write": ["right", "write"]}
    all_homophones = homophone_lookup.keys()

extension = lambda _: None


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


def do_extension(m):
    # noinspection PyProtectedMember
    count = max(utils.text_to_number([utils.parse_word(w) for w in m._words[1:]]), 1)
    for _ in range(count):
        extension(m)


supported_apps = {"com.microsoft.VSCode", "com.googlecode.iterm2"}
supported_apps.update(port_mapping.keys())


def not_supported_editor(app, _):
    if str(app.bundle) in supported_apps:
        return False
    return True


ctx = Context("editor", func=not_supported_editor)


def select_text_from_cursor(direction):
    # jcooper-korg from talon slack
    def fn(m):
        words = utils.parse_words(m)
        if not words:
            return
        if direction == "left":
            more = "home"
            back = "right"
        else:
            more = "end"
            back = "left"
        key = utils.join_words(words).lower()
        keys = homophone_lookup.get(key, [key])
        text = _get_line(direction, back, more)
        result = -1 if direction == "left" else len(text) + 1
        for needle in keys:
            find = text.find(needle)
            if direction == "left" and find > result:
                result = find
                key = needle
                # There could be a closer one...
                find = text.find(needle, result+1)
                while find > result:
                    result = find
                    find = text.find(needle, result + 1)
                break
            if direction == "right" and find == -1:
                continue
            if direction == "right" and find < result:
                result = find
                key = needle
                break
        if result == (-1 if direction == "left" else len(text) + 1):
            return
        _select_in_text(direction, key, result, text)
        global extension
        extension = lambda _: fn(m)
    return fn


def select_bounded_from_cursor(direction):
    # jcooper-korg from talon slack
    def fn(m):
        if direction == "left":
            more = "home"
            back = "right"
        else:
            more = "end"
            back = "left"
        keys = [alphabet[k] for k in m["editor.alphabet"]]
        regex = r"\b" + r"[^-_ .()]*?".join(
            keys
        )
        text = _get_line(direction, back, more)
        print(regex, text, direction)
        result = -1 if direction == "left" else len(text) + 1
        key = ""
        if direction == "left":
            print("going left")
            for hit in re.finditer(regex, text):
                result = hit.start()
                key = hit.string
                print(key, result, hit)
        else:
            match = re.search(regex, text)
            if match is None:
                return
            key = match.string
            result = match.start()
            print(key, result, match)
        if result == -1:
            return
        print(direction, regex, key, result, text)
        _select_in_text(direction, key, result, text)
        global extension
        extension = lambda _: fn(m)


    return fn


def _get_line(direction, back, more):
    press(direction, wait=2000)
    press(back, wait=2000)
    press("shift-" + more, wait=2000)
    with clip.capture() as s:
        press("cmd-c", wait=2000)
    press(back, wait=2000)
    text = s.get()

    return text


def _select_in_text(direction, key, result, text):
    if direction == "left":
        count = len(text) - result
    else:
        count = result
    # print(direction, text, keys, result, len(text), count)
    # cursor over to the found key text
    for i in range(0, count):
        press(direction, wait=0)
    # now select the matching key text
    for i in range(0, len(key)):
        press("shift-right")



ctx.keymap(
    {
        "phones last <dgndictation> [over]": [
            select_text_from_cursor("left"),
            lambda m: raise_homophones(m, is_selection=True),
        ],
        "phones next <dgndictation> [over]": [
            select_text_from_cursor("right"),
            lambda m: raise_homophones(m, is_selection=True),
        ],
        f"extend {utils.optional_numerals}": do_extension,
        # moving
        "go word left": extendable("alt-left"),
        "go word right": extendable("alt-right"),
        "go line start": extendable("cmd-left"),
        "go line end": extendable("cmd-right"),
        "go way left": extendable("cmd-left"),
        "go way right": extendable("cmd-right"),
        "go way down": extendable("cmd-down"),
        "go way up": extendable("cmd-up"),
        "go phrase left": [utils.select_last_insert, extendable("left")],
        # selecting
        "select all": [Key("cmd-a")],
        "(correct | select phrase)": utils.select_last_insert,
        "select last <dgndictation> [over]": select_text_from_cursor("left"),
        "select next <dgndictation> [over]": select_text_from_cursor("right"),
        "select last bounded {editor.alphabet}+": select_bounded_from_cursor("left"),
        "select next bounded {editor.alphabet}+": select_bounded_from_cursor("right"),
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
        "select way left": extendable("cmd-shift-left"),
        "select way right": extendable("cmd-shift-right"),
        "select way up": extendable("cmd-shift-up"),
        "select way down": extendable("cmd-shift-down"),
        # deleting
        "clear phrase": [utils.select_last_insert, extendable("backspace")],
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
        # clipboard
        "cut this": Key("cmd-x"),
        "copy this": Key("cmd-c"),
        "paste [here]": Key("cmd-v"),
        # Copying
        "copy phrase": [utils.select_last_insert, Key("cmd-c")],
        "copy all": [Key("cmd-a cmd-c")],
        "copy line": extendable("cmd-left cmd-left cmd-shift-right cmd-c cmd-right"),
        "copy word left": extendable("shift-alt-left cmd-c"),
        "copy word right": extendable("shift-alt-right cmd-c"),
        "copy way left": extendable("cmd-shift-left cmd-c"),
        "copy way right": extendable("cmd-shift-right cmd-c"),
        "copy way up": extendable("cmd-shift-up cmd-c"),
        "copy way down": extendable("cmd-shift-down cmd-c"),
        # Cutting
        "cut phrase": [utils.select_last_insert, Key("cmd-x")],
        "cut all": [Key("cmd-a cmd-x")],
        "cut line": extendable("cmd-left cmd-left cmd-shift-right cmd-x cmd-right"),
        "cut word left": extendable("shift-alt-left cmd-x"),
        "cut word right": extendable("shift-alt-right cmd-x"),
        "cut way left": extendable("cmd-shift-left cmd-x"),
        "cut way right": extendable("cmd-shift-right cmd-x"),
        "cut way up": extendable("cmd-shift-up cmd-x"),
        "cut way down": extendable("cmd-shift-down cmd-x"),
    }
)
ctx.set_list("alphabet", alphabet.keys())