from talon import app, clip, ui
from talon.voice import Context, Key

from ..utils import delay, text, vocab, word, i, numerals, parse_word, text_to_number, insert, text_with_leading


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
        # "over": delay(0.3),
        "literal <dgndictation>++": text,
        "say <dgndictation> [over]": text,
        # "sentence <dgndictation> [over]": sentence_text,  # Formatters.
        # "comma <dgndictation> [over]": [", ", text],
        # "period <dgndictation> [over]": [". ", text],
        # "more <dgndictation> [over]": [" ", text],
        "more <dgndictation> [over]": text_with_leading(" "),
        "word <dgnwords>": word,
        f"numeral {numerals}": type_number,
        "slap": [Key("cmd-right enter")],
        "cape": [Key("escape")],
        "pa": [Key("space")],
        "question [mark]": i("?"),
        "tilde": i("~"),
        "(bang | exclamation point)": i("!"),
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
        "(at sign | arobase)": i("@"),
        "ampersand": i("&"),
        "pipe": i("|"),
        "(dubquote | double quote)": i('"'),
        "triple tick": i("'''"),
        "triple quote": i('"""'),
        "swipe": [Key("right"), i(", ")],
        "item": i(", "),
        "value": i(": "),
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
        "(minus | subtract)": i(" - "),
        "add": i(" + "),
        "(times | multiply)": i(" * "),
        "(divide | divided by)": i(" / "),
        "modulo": i(" % "),
        "(minus | subtract) equals": i(" -= "),
        "(plus | add) equals": i(" += "),
        "(times | multiply) equals": i(" *= "),
        "divide equals": i(" /= "),
        "(mod | modulo) equals": i(" %= "),
        "is greater [than]": i(" > "),
        "is less [than]": i(" < "),
        "is equal [to]": i(" == "),
        "is not [equal] [to]": i(" != "),
        "is greater [than] or equal [to]": i(" >= "),
        "is less [than] or equal [to] ": i(" <= "),
        "to the power of": i(" ** "),
        ## Language specific, moved to language.py.
        # "logical and": i(" && "),
        # "logical or": i(" || "),
        "bitwise and": i(" & "),
        "bitwise or": i(" | "),
        "(piped | alternate)": i(" | "),
        "bitwise exclusive or": i(" ^ "),
        "[bitwise] left shift": i(" << "),
        "[bitwise] right shift": i(" >> "),
        "bitwise and equals": i(" &= "),
        "bitwise or equals": i(" |= "),
        "bitwise exclusive or equals": i(" ^= "),
        "[bitwise] left shift equals": i(" <<= "),
        "[bitwise] right shift equals": i(" >>= "),

        "[focus] next window": Key("cmd-`"),
        "[focus] last window": Key("cmd-shift-`"),
        "[focus] next app": Key("cmd-tab"),
        "[focus] last app": Key("cmd-shift-tab"),
        "[focus] next tab": Key("ctrl-tab"),
        "[focus] last tab": Key("ctrl-shift-tab"),
        "create tab": Key("cmd-t"),
        "create window": Key("cmd-n"),
        "undo": Key("cmd-z"),

        # Moved to amethyst.py
        # "next space": Key("cmd-alt-ctrl-right"),
        # "last space": Key("cmd-alt-ctrl-left"),
        "copy active bundle": copy_bundle,
    }
)
