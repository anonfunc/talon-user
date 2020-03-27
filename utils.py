import json
import os
import re
import string
import time
import typing as t

from talon import applescript, resource, cron, ctrl
from talon.voice import Str, press
from talon_plugins import eye_mouse, eye_zoom_mouse, microphone

ordinal_indexes = {
    "first": 0,
    "second": 1,
    "third": 2,
    "fourth": 3,
    "fifth": 4,
    "sixth": 5,
    "seventh": 6,
    "eighth": 7,
    "ninth": 8,
    "tenth": 9,
    "final": -1,
    "next": "next",  # Yeah, yeah, not a number.
    "last": "last",
    "this": "this",
}

mapping = {
    "semicolon": ";",
    "new-line": "\n",
    "new-paragraph": "\n\n",
    "dot": ".",
    "…": "...",
    "comma": ",",
    "question": "?",
    "exclamation": "!",
    "dash": "-",
}
punctuation = set(".,-!?")

try:
    vocab_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vocab.json")
    with resource.open(vocab_path) as fh:
        vocab = json.load(fh)
except FileNotFoundError:
    vocab = []


def add_vocab(words):
    global vocab
    vocab += [re.sub("[^a-zA-Z0-9]+", "", w) for w in words]
    vocab = sorted(list(set(vocab)))
    with open(vocab_path, "w") as f:
        json.dump(vocab, f, indent=0)


def parse_word(w):
    w = str(w).lstrip("\\").split("\\", 1)[0]
    w = mapping.get(w, w)
    # w = w.replace("-", "")  # hate dragon hyphenation.
    return w


def parse_words(m):
    try:
        # noinspection PyProtectedMember
        return list(map(parse_word, m.dgndictation[0]._words))
    except AttributeError:
        return []


def join_words(words, sep=" "):
    out = ""
    for i, w in enumerate(words):
        if i > 0 and w not in punctuation:
            out += sep
        out += w
    return out


last_insert = ""
reenable_job = None


def debounce_enable_job():
    global reenable_job
    if reenable_job is not None:
        cron.cancel(reenable_job)
        reenable_job = cron.after("3s", enable_tracking)


def enable_tracking():
    if not eye_mouse.control_mouse.enabled:
        eye_mouse.control_mouse.toggle()


def insert(s):
    global last_insert, reenable_job

    last_insert = s
    # if eye_zoom_mouse.zoom_mouse.enabled:
    #     eye_zoom_mouse.zoom_mouse.toggle()
    # if eye_mouse.control_mouse.enabled:
    #     eye_mouse.control_mouse.toggle()
    #     ctrl.cursor_visible(True)
    #     if reenable_job is None:
    #         reenable_job = cron.after("3s", enable_tracking)
    # elif reenable_job is not None:
    #     debounce_enable_job()
    Str(s)(None)


def i(s):
    return lambda _: insert(s)


def select_last_insert(_):
    for _ in range(len(last_insert)):
        press("left")
    for _ in range(len(last_insert)):
        press("shift-right")


def text(m):
    insert(join_words(parse_words(m)))
    # Add a universal fudge factor.
    time.sleep(0.2)

def sentence_text(m):
    words = parse_words(m)
    words[0] = str(words[0]).capitalize()
    insert(join_words(words))
    # Add a universal fudge factor.
    time.sleep(0.2)



def list_value(l, index=0):
    def _val(m):
        insert(m[l][index])

    return _val


def text_with_trailing_space(m):
    insert(join_words(parse_words(m)) + " ")


def text_with_leading_space(m):
    insert(" " + join_words(parse_words(m)))


def text_with_leading(leading):
    return lambda m: insert(leading + join_words(parse_words(m)))


def word(m):
    try:
        # noinspection PyProtectedMember
        insert(join_words(list(map(parse_word, m.dgnwords[0]._words))))
        # Universal fudge factor.
        time.sleep(0.2)
    except AttributeError:
        pass


def surround(by):
    def func(i, w, last):
        if i == 0:
            w = by + w
        if last:
            w += by
        return w

    return func


def rot13(_, w, __):
    out = ""
    for c in w.lower():
        if c in string.ascii_lowercase:
            c = chr((((ord(c) - ord("a")) + 13) % 26) + ord("a"))
        out += c
    return out


numeral_map = dict((str(n), n) for n in range(0, 20))
for n in range(20, 101, 10):
    numeral_map[str(n)] = n
for n in range(100, 1001, 100):
    numeral_map[str(n)] = n
for n in range(1000, 10001, 1000):
    numeral_map[str(n)] = n
numeral_map["oh"] = 0  # synonym for zero
numeral_map["and"] = None  # drop me

numerals = " (" + " | ".join(sorted(numeral_map.keys())) + ")+"
optional_numerals = " (" + " | ".join(sorted(numeral_map.keys())) + ")*"


def text_to_number(words):
    words = [parse_word(w).lower() for w in words]

    result = 0
    factor = 1
    for i, w in enumerate(reversed(words)):
        print(f"{i} {result} {factor} {w}")
        if w not in numerals:
            raise Exception("not a number: {}".format(words))

        number = numeral_map[w]
        if number is None:
            continue
        number = int(number)
        print(f"{i} {result} {factor} {w} {number}")
        if number > factor and number % factor == 0:
            result = result + number
        else:
            result = result + factor * number
        if i != 0:
            factor = (10 ** max(1, len(str(number).rstrip("0")))) * factor
        else:
            factor = (10 ** max(1, len(str(number)))) * factor
    return result


def text_to_range(words, delimiter="until"):
    tmp = [str(s).lower() for s in words]
    split = tmp.index(delimiter)
    start = text_to_number(words[:split])
    end = text_to_number(words[split + 1:])
    return start, end


def delay(amount):
    return lambda _: time.sleep(amount)


def use_mic(mic_name):
    mic = microphone.manager.active_mic()
    if mic is not None and mic.name == mic_name:
        return
    # noinspection PyUnresolvedReferences
    mics = {i.name: i for i in list(microphone.manager.menu.items)}
    if mic_name in mics:
        microphone.manager.menu_click(mics[mic_name])

def mic_uses_volume(settings: t.Dict[str, int]):
    mics = {i.name: i for i in list(microphone.manager.menu.items)}
    for m in settings:
        if m in mics:
            set_input_volume(settings[m])


def set_input_volume(m: int):
    applescript.run(f"set volume input volume {m}")