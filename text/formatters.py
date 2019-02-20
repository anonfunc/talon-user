import re

import talon.clip as clip
from talon.voice import Context, Str, Word, press

from ..utils import parse_word, surround, vocab

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
    "private": (True, lambda i, word, _: word if i == 0 else word if word.upper() == word else word.capitalize()),
    "public": (True, lambda i, word, _: word if word.upper() == word else word.capitalize()),
    # Call method: for driving jetbrains style fuzzy Complete -> .fuzCom
    "call": (True,  lambda i, word, _: "." + word[0:3] if i == 0 else word[0:3].capitalize()),
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
    return re.sub(r'[-_]', ' ', re.sub('(?!^)([A-Z0-9][a-z0-9]*)', r' \1', identifier))


def format_text(m):
    fmt = []
    # noinspection PyProtectedMember
    for w in m._words:
        if isinstance(w, Word) and str(w.word) != "over":
            # noinspection PyUnresolvedReferences
            fmt.append(w.word)
    try:
        # noinspection PyProtectedMember
        words = [str(s) for s in m.dgndictation[0]._words]
    except AttributeError:
        with clip.capture() as s:
            press("cmd-c", wait=2000)
        words = normalize(s.get()).split()

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
    Str(sep.join(words))(None)


ctx = Context("formatters")
ctx.vocab = vocab
ctx.keymap(
    {
        f"({' | '.join(formatters)})+ [<dgndictation>] [over]": format_text
    }
)
