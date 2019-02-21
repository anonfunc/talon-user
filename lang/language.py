# Language:
# Programming specific dictation, mostly that which could vary by language.
# Mostly keyword commands of the form "state <something>" so that the keywords in the syntax
# can be expressed with no ambiguity.  (Consider `state else` -> "else" vs `word else` -> "elves".)
from talon.voice import Context, Key

from ..utils import i

def extension_context(ext):
    def language_match(app, win):
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
ctx.keymap(
    {
        "state (def | deaf | deft)": i("def "),
        "state else if": i("elif "),
        "state if": i("if "),
        "state while": i(["while ()", Key("left")]),
        "state for": i("for "),
        "state import": i("import "),
        "state class": i("class "),
        "state (past | pass)": i("pass"),
        "state true": i("True"),
        "state false": i("False"),
    }
)

ctx = Context("golang", func=extension_context(".go"))
ctx.keymap(
    {
        # Many of these add extra terrible spacing under the assumption that
        # gofmt/goimports will erase it.
        "state (funk | func | fun)": i("func "),
        "state var": i("var "),
        "state break": i("break"),
        "state (chan | channel)": i(" chan "),
        "state go": i("go "),
        "state if": i("if "),
        "state else if": i(" else if "),
        "state else": i(" else "),
        "state while": i("while "),  # actually a live template for "for" with a single condition
        "state for": i("for "),
        "state for range": i("forr "),
        "state format": i("fmt"),
        "state switch": i("switch "),
        "state select": i("select "),
        "state (const | constant)": i(" const "),
        "state case": i(" case "),
        "state type": i(" type "),
        "state true": i(" true "),
        "state false": i(" false "),
        "state (start | struct | struck)": i(" struct "),
        "state interface": i(" interface{} "),
        "state string": i(" string "),
        "state (int | integer | ant)": i(" int "),
        "state (int | integer | ant) 64": i(" int64 "),
        "state slice": i(" []"),
        "state tag": [" ``", Key("left")],
        "state return": i(" return "),
        "map of string to string": i(" map[string]string "),
        "receive": i(" <- "),
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
