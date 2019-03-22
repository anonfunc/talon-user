# Language:
# Programming specific dictation, mostly that which could vary by language.
# Mostly keyword commands of the form "state <something>" so that the keywords in the syntax
# can be expressed with no ambiguity.  (Consider `state else` -> "else" vs `word else` -> "elves".)
from talon.voice import Context, Key

from ..text.formatters import GOLANG_PRIVATE, DOT_SEPARATED, DOWNSCORE_SEPARATED, SENTENCE, GOLANG_PUBLIC, LOWSMASH, formatted_text
from ..utils import i

def extension_context(ext):
    def language_match(app, win):
        if win is None:
            return False
        title = win.title
        filename = ""
        #print("Window title:" + title)
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
        "state comment": i("  # "),
        "line comment <dgndictation>": [Key("cmd-right"), i("  # "), formatted_text(SENTENCE)],
        "state (def | deaf | deft)": i("def "),
        "function <dgndictation>": [i("def "), formatted_text(DOWNSCORE_SEPARATED), i("():"), Key("left left")],
        "method <dgndictation>": [i("def "), formatted_text(DOWNSCORE_SEPARATED), i("(self, ):"), Key("left left")],
        "state else if": i("elif "),
        "state if": i("if "),
        "if <dgndictation>": [i("if "), formatted_text(DOWNSCORE_SEPARATED)],
        "state while": i("while "),
        "while <dgndictation>": [i("while "), formatted_text(DOWNSCORE_SEPARATED)],
        "state for": i("for "),
        "for <dgndictation>": [i("for "), formatted_text(DOWNSCORE_SEPARATED)],
        "state import": i("import "),
        "import <dgndictation>": [i("for "), formatted_text(DOT_SEPARATED)],
        "state class": i("class "),
        "class <dgndictation>": [i("class "), formatted_text(GOLANG_PUBLIC), i(":\n")],
        "state (past | pass)": i("pass"),
        "state true": i("True"),
        "state false": i("False"),
        "item <dgndictation>": [i(", "), formatted_text(DOWNSCORE_SEPARATED)],
    }
)

ctx = Context("golang", func=extension_context(".go"))
ctx.vocab = [
    'nil',
    'context',
]
ctx.keymap(
    {
        # Many of these add extra terrible spacing under the assumption that
        # gofmt/goimports will erase it.
        "state comment": i("  // "),
        "line comment <dgndictation>": [Key("cmd-right"), i("  // "), formatted_text(SENTENCE)],
        "state context": i("ctx"),
        "state (funk | func | fun)": i("func "),
        "function <dgndictation>": [i("func "), formatted_text(GOLANG_PRIVATE), i("()"), Key("left left")],
        "method <dgndictation>": [i("meth "), formatted_text(GOLANG_PRIVATE)],
        "state var": i("var "),
        "variable <dgndictation>": [i("var "), formatted_text(GOLANG_PRIVATE), i(" ")],
        "set <dgndictation>": [formatted_text(GOLANG_PRIVATE), i(" := ")],
        "state break": i("break"),
        "state (chan | channel)": i(" chan "),
        "state go": i("go "),
        "state if": i("if "),
        "if <dgndictation>": [i("if "), formatted_text(GOLANG_PRIVATE)],
        "state else if": i(" else if "),
        "else if <dgndictation>": [i(" else if "), formatted_text(GOLANG_PRIVATE)],
        "state else": i(" else "),
        "else <dgndictation>": [i(" else {}"), Key("left enter"), formatted_text(GOLANG_PRIVATE)],
        "state while": i("while "),  # actually a live template for "for" with a single condition
        "while <dgndictation>": [i("while "), formatted_text(GOLANG_PRIVATE)],
        "state for": i("for "),
        "for <dgndictation>": [i("for "), formatted_text(GOLANG_PRIVATE)],
        "state for range": i("forr "),
        "range <dgndictation>": [i("forr "), formatted_text(GOLANG_PRIVATE)],
        "state format": i("fmt"),
        "format <dgndictation>": [i("fmt."), formatted_text(GOLANG_PUBLIC)],
        "state switch": i("switch "),
        "switch <dgndictation>": [i("switch "), formatted_text(GOLANG_PRIVATE)],
        "state select": i("select "),
        # "select <dgndictation>": [i("select "), formatted_text(GOLANG_PRIVATE)],
        "state (const | constant)": i(" const "),
        "constant <dgndictation>": [i("const "), formatted_text(GOLANG_PUBLIC)],
        "state case": i(" case "),
        "case <dgndictation>": [i("case "), formatted_text(GOLANG_PRIVATE)],
        "state type": i(" type "),
        "type <dgndictation>": [i("type "), formatted_text(GOLANG_PUBLIC)],
        "state true": i(" true "),
        "state false": i(" false "),
        "state (start | struct | struck)":  [i(" struct {}"), Key("left enter")],
        "(struct | struck) <dgndictation>": [i(" struct {}"), Key("left enter"), formatted_text(GOLANG_PUBLIC)],
        "state empty interface": i(" interface{} "),
        "state interface": [i(" interface {}"), Key("left enter")],
        "interface <dgndictation>": [i(" interface {}"), Key("left enter"), formatted_text(GOLANG_PUBLIC)],
        "state string": i(" string "),
        "state (int | integer | ant)": i(" int "),
        "state slice": i(" []"),
        "state (no | nil)": i("nil"),
        "state (int | integer | ant) 64": i(" int64 "),
        "state tag": [i(" ``"), Key("left")],
        "tag <dgndictation>": [i(" ``"), Key("left"), formatted_text(LOWSMASH), i(':""'), Key("left")],
        "state return": i(" return "),
        "return  <dgndictation>": [i("return "), formatted_text(GOLANG_PRIVATE)],
        "map of string to string": i(" map[string]string "),
        "receive": i(" <- "),
        "state (air | err)": i("err"),
        "item <dgndictation>": [i(", "), formatted_text(GOLANG_PRIVATE)],
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
