from talon import app, clip, ui
from talon.voice import Context, Key

from ..utils import text, vocab, word, i, numerals, parse_word, text_to_number, insert


def copy_bundle(_):
    bundle = ui.active_app().bundle
    clip.set(bundle)
    app.notify("Copied app bundle", body="{}".format(bundle))


def type_number(m):
    # noinspection PyProtectedMember
    count = text_to_number([parse_word(w) for w in m._words[1:]])
    insert(str(count))


ctx = Context("input")
ctx.vocab = vocab
ctx.keymap(
    {
        "say <dgndictation> [over]": text,
        # "sentence <dgndictation> [over]": sentence_text,  # Formatters.
        "comma <dgndictation> [over]": [", ", text],
        "period <dgndictation> [over]": [". ", text],
        # "more <dgndictation> [over]": [" ", text],
        "word <dgnwords>": word,
        f"numeral {numerals}": type_number,
        "slap": [Key("cmd-right enter")],
        "cape": [Key("escape")],
        "pa": [Key("space")],
        "question [mark]": i("?"),
        "tilde": i("~"),
        "(bang | exclamation point | not)": i("!"),
        "dollar [sign]": i("$"),
        "downscore": i("_"),
        "colon": i(":"),
        "(paren | left paren)": i("("),
        "(rparen | are paren | right paren)": i(")"),
        "(brace | left brace)": i("{"),
        "(rbrace | are brace | right brace)": i("}"),
        # Square Brackets are in basic_keys.py!
        # "(square | left square)": "[",
        # "(rsquare | are square | right square)": "]",
        "(angle | left angle | less than)": i("<"),
        "(rangle | are angle | right angle | greater than)": i(">"),
        "(star | asterisk)": i("*"),
        "(pound | hash [sign] | octo | thorpe | number sign)": i("#"),
        "(percent [sign] | modulo)": i("%"),
        "caret": i("^"),
        "at sign": i("@"),
        "(and sign | ampersand | amper)": i("&"),
        "pipe": i("|"),
        "(dubquote | double quote)": i('"'),
        "triple tick": i("'''"),
        "triple quote": i('"""'),
        "swipe": [Key("right"), i(", ")],
        "item": i(", "),
        # "space": " ",  # basic_keys.py
        "(args | arguments)": ["()", Key("left")],
        "index": ["[]", Key("left")],
        "block": [" {}", Key("left enter")],
        "empty array": i("[]"),
        "(empty dict | empty dictionary)": i("{}"),
        "plus": i("+"),
        "arrow": i("->"),
        # "call": "()",
        "indirect": i("&"),
        "dereference": i("*"),
        "assign": i(" = "),
        "[op] set to": i(" := "),
        "op (minus | subtract)": i(" - "),
        "op (plus | add)": i(" + "),
        "op (times | multiply)": i(" * "),
        "op divide": i(" / "),
        "op mod": i(" % "),
        "[op] (minus | subtract) equals": i(" -= "),
        "[op] (plus | add) equals": i(" += "),
        "[op] (times | multiply) equals": i(" *= "),
        "[op] divide equals": i(" /= "),
        "[op] mod equals": i(" %= "),
        "(op | is) greater [than]": i(" > "),
        "(op | is) less [than]": i(" < "),
        "(op | is) equal": i(" == "),
        "(op | is) not equal": i(" != "),
        "(op | is) greater [than] or equal": i(" >= "),
        "(op | is) less [than] or equal": i(" <= "),
        "(op (power | exponent) | to the power [of])": i(" ** "),
        "op and": i(" && "),
        "op or": i(" || "),
        "[op] (logical | bitwise) and": i(" & "),
        "[op] (logical | bitwise) or": i(" | "),
        "op pipe": i(" | "),
        "(op | logical | bitwise) (ex | exclusive) or": i(" ^ "),
        "[(op | logical | bitwise)] (left shift | shift left)": i(" << "),
        "[(op | logical | bitwise)] (right shift | shift right)": i(" >> "),
        "(op | logical | bitwise) and equals": i(" &= "),
        "(op | logical | bitwise) or equals": i(" |= "),
        "(op | logical | bitwise) (ex | exclusive) or equals": i(" ^= "),
        "[(op | logical | bitwise)] (left shift | shift left) equals": i(" <<= "),
        "[(op | logical | bitwise)] (right shift | shift right) equals": i(" >>= "),
        "focus next window": Key("cmd-`"),
        "focus last window": Key("cmd-shift-`"),
        "focus next app": Key("cmd-tab"),
        "focus last app": Key("cmd-shift-tab"),
        "focus next tab": Key("ctrl-tab"),
        "focus last tab": Key("ctrl-shift-tab"),
        "create tab": Key("cmd-t"),
        "create window": Key("cmd-n"),
        "undo": Key("cmd-z"),
        # Moved to amethyst.py
        # "next space": Key("cmd-alt-ctrl-right"),
        # "last space": Key("cmd-alt-ctrl-left"),
        "copy active bundle": copy_bundle,
    }
)
