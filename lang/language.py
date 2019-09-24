# Language:
# Programming specific dictation, mostly that which could vary by language.
# Mostly keyword commands of the form "state <something>" so that the keywords in the syntax
# can be expressed with no ambiguity.  (Consider `state else` -> "else" vs `word else` -> "elves".)
import os

from talon.voice import Context, Key

from ..text.formatters import (
    GOLANG_PRIVATE,
    DOT_SEPARATED,
    DOWNSCORE_SEPARATED,
    SENTENCE,
    GOLANG_PUBLIC,
    SLICE,
    LOWSMASH,
    JARGON,
    formatted_text,
)
from ..utils import i, delay, text_with_leading

def not_extension_context(*exts):
    def language_match(app, win):
        if win is None:
            return True
        title = win.title
        filename = ""
        # print("Window title:" + title)
        if app.bundle == "com.microsoft.VSCode":
            if u"\u2014" in title:
                filename = title.split(u" \u2014 ", 1)[0]  # Unicode em dash!
            elif "-" in title:
                filename = title.split(u" - ", 1)[0]
        elif app.bundle == "com.apple.Terminal":
            parts = title.split(" \u2014 ")
            if len(parts) >= 2 and parts[1].startswith(("vi ", "vim ")):
                filename = parts[1].split(" ", 1)[1]
            else:
                return True
        elif str(app.bundle).startswith("com.jetbrains."):
            filename = title.split(" - ")[-1]
            filename = filename.split(" [")[0]
        elif win.doc:
            filename = win.doc
        else:
            return True
        filename = filename.strip()
        _, ext = os.path.splitext(filename)
        # print(ext, exts, ext not in exts)
        return ext not in exts

    return language_match


def extension_context(ext):
    def language_match(app, win):
        if win is None:
            return False
        title = win.title
        filename = ""
        # print("Window title:" + title)
        if app.bundle == "com.microsoft.VSCode":
            if u"\u2014" in title:
                filename = title.split(u" \u2014 ", 1)[0]  # Unicode em dash!
            elif "-" in title:
                filename = title.split(u" - ", 1)[0]
        elif app.bundle == "com.apple.Terminal":
            parts = title.split(" \u2014 ")
            if len(parts) >= 2 and parts[1].startswith(("vi ", "vim ")):
                filename = parts[1].split(" ", 1)[1]
            else:
                return False
        elif str(app.bundle).startswith("com.jetbrains."):
            filename = title.split(" - ")[-1]
            filename = filename.split(" [")[0]
        elif win.doc:
            filename = win.doc
        else:
            return False
        filename = filename.strip()
        return filename.endswith(ext)

    return language_match


ctx = Context("python", func=extension_context(".py"))
# ctx.vocab = [
#     '',
#     '',
# ]
# ctx.vocab_remove = ['']

# Most of the formatted insertions are downscore_separated under the assumption
# that you are operating on a locally scoped variable.
ctx.keymap(
    {
        "[logical] and": i(" and "),
        "logical or": i(" or "),
        "state comment": i("# "),
        "[line] comment <dgndictation> [over]": [
            Key("cmd-right"),
            i("  # "),
            formatted_text(SENTENCE),
        ],
        # "add comment <dgndictation> [over]": [
        #     Key("cmd-right"),
        #     text_with_leading(" # "),
        # ],
        "state (def | deaf | deft)": i("def "),
        "function <dgndictation> [over]": [
            i("def "),
            formatted_text(DOWNSCORE_SEPARATED),
            i("():"),
            Key("left left"),
        ],
        "method <dgndictation> [over]": [
            i("def "),
            formatted_text(DOWNSCORE_SEPARATED),
            i("(self, ):"),
            Key("left left"),
        ],
        "state else if": i("elif "),
        "state if": i("if "),
        "is not none": i(" is not None"),
        "is none": i(" is None"),
        "if <dgndictation> [over]": [i("if "), formatted_text(DOWNSCORE_SEPARATED)],
        "state while": i("while "),
        "while <dgndictation> [over]": [
            i("while "),
            formatted_text(DOWNSCORE_SEPARATED),
        ],
        "state for": i("for "),
        "for <dgndictation> [over]": [i("for "), formatted_text(DOWNSCORE_SEPARATED)],
        "body": [Key("cmd-right : enter")],
        "state import": i("import "),
        "import <dgndictation> [over]": [i("for "), formatted_text(DOT_SEPARATED)],
        "state class": i("class "),
        "class <dgndictation> [over]": [
            i("class "),
            formatted_text(GOLANG_PUBLIC),
            i(":\n"),
        ],
        "state (past | pass)": i("pass"),
        "state true": i("True"),
        "state false": i("False"),
        "state none": i("None"),
        "item <dgndictation> [over]": [i(", "), formatted_text(DOWNSCORE_SEPARATED)],
    }
)

ctx = Context("golang", func=extension_context(".go"))
ctx.vocab = ["nil", "context", "lambda", "init"]
ctx.vocab_remove = ["Linda", "Doctor", "annette"]
ctx.keymap(
    {
        "[logical] and": i(" && "),
        "logical or": i(" || "),
        # Many of these add extra terrible spacing under the assumption that
        # gofmt/goimports will erase it.
        "state comment": i("// "),
        "[line] comment <dgndictation>": [
            Key("cmd-right"),
            i(" // "),
            formatted_text(SENTENCE),
        ],
        # "add comment <dgndictation> [over]": [
        #     Key("cmd-right"),
        #     text_with_leading(" // "),
        # ],
        "[state] context": i("ctx"),
        "state (funk | func | fun)": i("func "),
        "function (Annette | init) [over]": [
            i("func init() {\n"),
        ],
        "function <dgndictation> [over]": [
            i("func "),
            formatted_text(GOLANG_PRIVATE),
            i("("),
            delay(0.1),
        ],
        "method <dgndictation> [over]": [
            i("meth "),
            formatted_text(GOLANG_PRIVATE),
            delay(0.1),
        ],
        "state var": i("var "),
        "variable <dgndictation> [over]": [
            i("var "),
            formatted_text(GOLANG_PRIVATE),
            i(" "),
            delay(0.1),
        ],
        # "set <dgndictation> [over]": [
        #     formatted_text(GOLANG_PRIVATE),
        #     i(" := "),
        #     delay(0.1),
        # ],
        "state break": i("break"),
        "state (chan | channel)": i(" chan "),
        "state go": i("go "),
        "state if": i("if "),
        "if <dgndictation> [over]": [i("if "), formatted_text(GOLANG_PRIVATE)],
        "state else if": i(" else if "),
        "else if <dgndictation> [over]": [
            i(" else if "),
            formatted_text(GOLANG_PRIVATE),
        ],
        "state else": i(" else "),
        "else <dgndictation> [over]": [
            i(" else {"),
            Key("enter"),
            formatted_text(GOLANG_PRIVATE),
        ],
        "state while": i(
            "while "
        ),  # actually a live template for "for" with a single condition
        "while <dgndictation> [over]": [i("while "), formatted_text(GOLANG_PRIVATE)],
        "state for": i("for "),
        "for <dgndictation> [over]": [i("for "), formatted_text(GOLANG_PRIVATE)],
        "state for range": i("forr "),
        "range <dgndictation> [over]": [i("forr "), formatted_text(GOLANG_PRIVATE)],
        "state format": i("fmt"),
        "format <dgndictation> [over]": [i("fmt."), formatted_text(GOLANG_PUBLIC)],
        "state switch": i("switch "),
        "switch <dgndictation> [over]": [i("switch "), formatted_text(GOLANG_PRIVATE)],
        "state select": i("select "),
        # "select <dgndictation>": [i("select "), formatted_text(GOLANG_PRIVATE)],
        "state (const | constant)": i(" const "),
        "constant <dgndictation> [over]": [i("const "), formatted_text(GOLANG_PUBLIC)],
        "state case": i(" case "),
        "state default": i(" default:"),
        "case <dgndictation> [over]": [i("case "), formatted_text(GOLANG_PRIVATE)],
        "state type": i(" type "),
        "type <dgndictation> [over]": [i("type "), formatted_text(GOLANG_PUBLIC)],
        "state true": i(" true "),
        "state false": i(" false "),
        "state (start | struct | struck)": [i(" struct {"), Key("enter")],
        "(struct | struck) <dgndictation> [over]": [
            i(" struct {"),
            Key("enter"),
            formatted_text(GOLANG_PUBLIC),
        ],
        "[state] empty interface": i(" interface{} "),
        "state interface": [i(" interface {"), Key("enter")],
        "interface <dgndictation> [over]": [
            i(" interface {"),
            Key("enter"),
            formatted_text(GOLANG_PUBLIC),
        ],
        "state string": i(" string "),
        "[state] (int | integer | ant)": i(" int "),
        "state slice": i(" []"),
        "[state] (no | nil)": i("nil"),
        "state (int | integer | ant) 64": i(" int64 "),
        "state tag": [i(" ``"), Key("left")],
        "tag <dgndictation> [over]": [
            i(" `"),
            delay(0.1),
            formatted_text(LOWSMASH, JARGON),
            i(' '),
            delay(0.1),
        ],
        "state return": i(" return "),
        "return  <dgndictation> [over]": [i("return "), formatted_text(GOLANG_PRIVATE)],
        "map of string to string": i(" map[string]string "),
        "map of <dgndictation> [over]": [
            i("map["),
            formatted_text(GOLANG_PRIVATE),
            Key("right"),
            delay(0.1),
        ],
        "receive": i(" <- "),
        "make": i("make("),
        "loggers [<dgndictation>] [over]": [i("logrus."), formatted_text(GOLANG_PUBLIC)],
        "length <dgndictation> [over]": [i("len("), formatted_text(GOLANG_PRIVATE)],
        "append <dgndictation> [over]": [i("append("), formatted_text(GOLANG_PRIVATE)],
        "state (air | err)": i("err"),
        "error": i(" err "),
        "loop over <dgndictation> [over]": [formatted_text(GOLANG_PRIVATE), i(".forr ")],
        "item <dgndictation> [over]": [i(", "), formatted_text(GOLANG_PRIVATE)],
        "value <dgndictation> [over]": [i(": "), formatted_text(GOLANG_PRIVATE)],
    }
)

ctx = Context("generic", func=not_extension_context(".go", ".py"))
ctx.vocab = ["nil", "context", "lambda", "init"]
ctx.vocab_remove = ["Linda", "Doctor", "annette"]
ctx.keymap(
    {
        "[logical] and": i(" && "),
        "logical or": i(" || "),
    }
)

ctx = Context("jargon")
ctx.keymap(
    {
        "state jason": i("json"),
        "state (oct a | okta | octa)": i("okta"),
        "state (a w s | aws)": i("aws"),
        "state bite": i("byte"),
        "state bites": i("bytes"),
        "state state": i("state"),
    }
)
