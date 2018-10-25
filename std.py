from talon.voice import Word, Context, Key, Rep, RepPhrase, Str, press
from talon import app, ctrl, clip, ui
import string

from user.utility import (
    parse_word,
    parse_words,
    rot13,
    sentence_text,
    surround,
    text,
    word,
)

mapping = {"semicolon": ";", "new-line": "\n", "new-paragraph": "\n\n"}
punctuation = set(".,-!?")


formatters = {
    "dunder": (
        True,
        lambda i, word, last: ("__%s" % word if i == 0 else word)
        + ("__" if last else ""),
    ),
    "camel": (True, lambda i, word, _: word if i == 0 else word.capitalize()),
    "snake": (True, lambda i, word, _: word if i == 0 else "_" + word),
    "smash": (True, lambda i, word, _: word),
    # spinal or kebab?
    "kebab": (True, lambda i, word, _: word if i == 0 else "-" + word),
    "spinal": (True, lambda i, word, _: word if i == 0 else "-" + word),
    # 'sentence':  (False, lambda i, word, _: word.capitalize() if i == 0 else word),
    "title": (False, lambda i, word, _: word.capitalize()),
    "allcaps": (False, lambda i, word, _: word.upper()),
    "dubstring": (False, surround('"')),
    "string": (False, surround("'")),
    "padded": (False, surround(" ")),
    "rot-thirteen": (False, rot13),
}

def FormatText(m):
    fmt = []
    for w in m._words:
        if isinstance(w, Word):
            fmt.append(w.word)
    try:
        words = parse_words(m)
    except AttributeError:
        with clip.capture() as s:
            press("cmd-c")
        words = s.get().split(" ")
        if not words:
            return

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

def copy_bundle(m):
    bundle = ui.active_app().bundle
    clip.set(bundle)
    app.notify('Copied app bundle', body='{}'.format(bundle))

ctx = Context("input")

ctx.keymap(
    {
        "say <dgndictation> [over]": text,
        "sentence <dgndictation> [over]": sentence_text,
        "comma <dgndictation> [over]": [", ", text],
        "period <dgndictation> [over]": [". ", sentence_text],
        "more <dgndictation> [over]": [" ", text],
        "word <dgnwords>": word,
        "(%s)+ [<dgndictation>]" % (" | ".join(formatters)): FormatText,
        "tab": Key("tab"),
        "left": Key("left"),
        "right": Key("right"),
        "up": Key("up"),
        "down": Key("down"),
        "delete": Key("backspace"),
        "slap": [Key("cmd-right enter")],
        "enter": Key("enter"),
        "escape": Key("esc"),
        "question [mark]": "?",
        "tilde": "~",
        "(bang | exclamation point)": "!",
        "dollar [sign]": "$",
        "downscore": "_",
        "(semi | semicolon)": ";",
        "colon": ":",
        "(square | left square [bracket])": "[",
        "(rsquare | are square | right square [bracket])": "]",
        "(paren | left paren)": "(",
        "(rparen | are paren | right paren)": ")",
        "(brace | left brace)": "{",
        "(rbrace | are brace | right brace)": "}",
        "(angle | left angle | less than)": "<",
        "(rangle | are angle | right angle | greater than)": ">",
        "(star | asterisk)": "*",
        "(pound | hash [sign] | octo | thorpe | number sign)": "#",
        "percent [sign]": "%",
        "caret": "^",
        "at sign": "@",
        "(and sign | ampersand | amper)": "&",
        "pipe": "|",
        "(dubquote | double quote)": '"',
        "quote": "'",
        "triple quote": "'''",
        "(dot | period)": ".",
        "comma": ",",
        "swipe": ", ",
        "(space | skoosh)": " ",
        "[forward] slash": "/",
        "backslash": "\\",
        "(dot dot | dotdot)": "..",
        # "cd": "cd ",
        # "cd talon home": "cd {}".format(TALON_HOME),
        # "cd talon user": "cd {}".format(TALON_USER),
        # "cd talon plugins": "cd {}".format(TALON_PLUGINS),
        # "run make (durr | dear)": "mkdir ",
        # "run git": "git ",
        # "run git clone": "git clone ",
        # "run git diff": "git diff ",
        # "run git commit": "git commit ",
        # "run git push": "git push ",
        # "run git pull": "git pull ",
        # "run git status": "git status ",
        # "run git add": "git add ",
        # "run (them | vim)": "vim ",
        # "run ellis": "ls\n",
        # "dot pie": ".py",
        # "run make": "make\n",
        # "run jobs": "jobs\n",
        # "const": "const ",
        # "static": "static ",
        "(args | arguments)": ["()", Key("left")],
        "index": ["[]", Key("left")],
        "block": [" {}", Key("left enter enter up tab")],
        "empty array": "[]",
        "(empty dict | empty dictionary)": "{}",
        "equals": "=",
        "(minus | dash)": "-",
        "plus": "+",
        "arrow": "->",
        "call": "()",
        "indirect": "&",
        "dereference": "*",
        "(op equals | assign)": " = ",
        "set to": " := ",
        "op (minus | subtract)": " - ",
        "op (plus | add)": " + ",
        "op (times | multiply)": " * ",
        "op divide": " / ",
        "op mod": " % ",
        "[op] (minus | subtract) equals": " -= ",
        "[op] (plus | add) equals": " += ",
        "[op] (times | multiply) equals": " *= ",
        "[op] divide equals": " /= ",
        "[op] mod equals": " %= ",
        "(op | is) greater [than]": " > ",
        "(op | is) less [than]": " < ",
        "(op | is) equal": " == ",
        "(op | is) not equal": " != ",
        "(op | is) greater [than] or equal": " >= ",
        "(op | is) less [than] or equal": " <= ",
        "(op (power | exponent) | to the power [of])": " ** ",
        "op and": " && ",
        "op or": " || ",
        "[op] (logical | bitwise) and": " & ",
        "[op] (logical | bitwise) or": " | ",
        "(op | logical | bitwise) (ex | exclusive) or": " ^ ",
        "[(op | logical | bitwise)] (left shift | shift left)": " << ",
        "[(op | logical | bitwise)] (right shift | shift right)": " >> ",
        "(op | logical | bitwise) and equals": " &= ",
        "(op | logical | bitwise) or equals": " |= ",
        "(op | logical | bitwise) (ex | exclusive) or equals": " ^= ",
        "[(op | logical | bitwise)] (left shift | shift left) equals": " <<= ",
        "[(op | logical | bitwise)] (right shift | shift right) equals": " >>= ",
        "new window": Key("cmd-n"),
        "next window": Key("cmd-`"),
        "last window": Key("cmd-shift-`"),
        "(next app | swick)": Key("cmd-tab"),
        "last app": Key("cmd-shift-tab"),
        "next tab": Key("ctrl-tab"),
        "new tab": Key("cmd-t"),
        "(dizzle | undo)": Key("cmd-z"),
        "last tab": Key("ctrl-shift-tab"),
        "next space": Key("cmd-alt-ctrl-right"),
        "last space": Key("cmd-alt-ctrl-left"),
        "page down": [Key("pagedown")],
        "page up": [Key("pageup")],
        'copy active bundle': copy_bundle,
    }
)
