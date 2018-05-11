from talon.voice import Word, Context, Key, Rep, Str, press
from talon import ctrl
from talon_init import TALON_HOME, TALON_PLUGINS, TALON_USER
import string


from user.utility import *

alpha_alt = (
    "air bat cap die each fail gone harm ice jury crash look "
    "mad near odd pit quest red sun trap urge vest whale box yes zip"
).split()
alnum = list(zip(alpha_alt, string.ascii_lowercase)) + [
    (str(i), str(i)) for i in range(0, 10)
]

alpha = {}
alpha.update(dict(alnum))
alpha.update(
    {
        "ship %s" % word: letter
        for word, letter in zip(alpha_alt, string.ascii_uppercase)
    }
)

alpha.update({"control %s" % k: Key("ctrl-%s" % v) for k, v in alnum})
alpha.update({"command %s" % k: Key("cmd-%s" % v) for k, v in alnum})
alpha.update({"command shift %s" % k: Key("ctrl-shift-%s" % v) for k, v in alnum})
alpha.update({"command control %s" % k: Key("ctrl-ctrl-%s" % v) for k, v in alnum})
alpha.update({"command alt %s" % k: Key("ctrl-alt-%s" % v) for k, v in alnum})
alpha.update({"alt %s" % k: Key("alt-%s" % v) for k, v in alnum})

ctx = Context("input")

keymap = {}
keymap.update(alpha)
keymap.update(
    {
        "phrase <dgndictation> [over]": text,
        "word <dgnwords>": word,
        # Dictation
        "sentence <dgndictation> [over]": sentence_text,
        "comma <dgndictation> [over]": [", ", text],
        "period <dgndictation> [over]": [". ", sentence_text],
        "more <dgndictation> [over]": [" ", text],
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
        "space": " ",
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
        "args": ["()", Key("left")],
        "index": ["[]", Key("left")],
        "block": [" {}", Key("left enter enter up tab")],
        "empty array": "[]",
        "empty dict": "{}",
        "equals": "=",
        "(minus | dash)": "-",
        "plus": "+",
        "arrow": "->",
        "call": "()",
        "indirect": "&",
        "dereference": "*",
        "(op equals | assign)": " = ",
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
        "scroll down": [Key("pagedown")],
        "scroll up": [Key("pageup")],
        "tab": Key("tab"),
        "left": Key("left"),
        "right": Key("right"),
        "up": Key("up"),
        "down": Key("down"),
        "delete": Key("backspace"),
        "enter": Key("enter"),
        "escape": Key("esc"),
    }
)
ctx.keymap(keymap)
