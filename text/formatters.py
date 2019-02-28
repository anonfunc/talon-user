import re

import talon.clip as clip
from talon.voice import Context, Word, press

from ..utils import parse_word, surround, vocab, parse_words, insert

formatters = {
    # Smashed
    "acronym": (True, lambda i, word, _: word[0:1].upper()),
    "tree": (True, lambda i, word, _: word[0:3] if i == 0 else ""),
    "quad": (True, lambda i, word, _: word[0:4] if i == 0 else ""),
    "dunder": (
        True,
        lambda i, word, last: ("__%s" % word if i == 0 else word)
        + ("__" if last else ""),
    ),
    "camel": (True, lambda i, word, _: word if i == 0 else word.capitalize()),
    # Golang private/public conventions prefer SendHTML to SendHtml sendHtml
    "private": (
        True,
        lambda i, word, _: word
        if i == 0
        else word
        if word.upper() == word
        else word.capitalize(),
    ),
    "public": (
        True,
        lambda i, word, _: word if word.upper() == word else word.capitalize(),
    ),
    # Call method: for driving jetbrains style fuzzy Complete -> .fuzCom
    "call": (
        True,
        lambda i, word, _: "." + word[0:3] if i == 0 else word[0:3].capitalize(),
    ),
    "snake": (True, lambda i, word, _: word if i == 0 else "_" + word),
    "smash": (True, lambda i, word, _: word),
    "spine": (True, lambda i, word, _: word if i == 0 else "-" + word),
    # Spaced
    "sentence": (False, lambda i, word, _: word.capitalize() if i == 0 else word),
    "title": (False, lambda i, word, _: word.capitalize()),
    "allcaps": (False, lambda i, word, _: word.upper()),
    "lowcaps": (False, lambda i, word, _: word.lower()),
    "string": (False, surround('"')),
    "ticks": (False, surround("'")),
    "backticks": (False, surround("`")),
    "padded": (False, surround(" ")),
}


def normalize(identifier):
    # https://stackoverflow.com/questions/29916065/how-to-do-camelcase-split-in-python
    return re.sub(r"[-_]", " ", re.sub("(?!^)([A-Z0-9][a-z0-9]*)", r" \1", identifier))


def format_text(m):
    fmt = []
    # noinspection PyProtectedMember
    for w in m._words:
            # noinspection PyUnresolvedReferences
        if isinstance(w, Word) and parse_word(w.word) != "over":
            # noinspection PyUnresolvedReferences
            fmt.append(w.word)
    words = parse_words(m)
    if not words:
        with clip.capture() as s:
            press("cmd-c", wait=2000)
        words = normalize(s.get()).split()
    if not words:
        words = [""]

    tmp = []
    spaces = True
    for i, word in enumerate(words):
        word = parse_word(word)
        for name in reversed(fmt):
            smash, func = formatters[name]
            word = func(i, word, i == len(words) - 1)
            spaces = spaces and not smash
        tmp.append(word)
    words = tmp

    sep = " "
    if not spaces:
        sep = ""
    insert(sep.join(words))


ctx = Context("formatters")
ctx.vocab = vocab
ctx.keymap({f"({' | '.join(formatters)})+ [<dgndictation>] [over]": format_text})
