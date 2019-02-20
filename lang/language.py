from talon.voice import Context, Key


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
        "state (def | deaf | deft)": "def ",
        "state else if": "elif ",
        "state if": "if ",
        "state while": ["while ()", Key("left")],
        "state for": "for ",
        "state import": "import ",
        "state class": "class ",
        "state (past | pass)": "pass",
        "state true": "True",
        "state false": "False",
    }
)

ctx = Context("golang", func=extension_context(".go"))
ctx.keymap(
    {
        "state (funk | func | fun)": "func ",
        "state var": "var ",
        "state break": "break",
        "state if": "if ",
        "state else if": " else if ",
        "state else": " else ",
        "state while": "while ",  # actually a live template for "for" with a single condition
        "state for": "for ",
        "state for range": "forr ",
        "state format": "fmt",
        "state switch": "switch ",
        "state (const | constant)": "const ",
        "state case": "case ",
        "state type": "type ",
        "state true": "true",
        "state false": "false",
        "state (start | struct | struck)": " struct ",
        "state interface": " interface{} ",
        "state string": " string ",
        "state (int | integer | ant)": " int ",
        "state (int | integer | ant) 64": " int64 ",
        "state slice": "[]",
        "state tag": ["``", Key("left")],
        "state return": "return ",
        "map of string to string": " map[string]string ",
        "go dot": Key("cmd-right ."),
    }
)

ctx = Context("jargon")
ctx.keymap(
    {
        "state jason": "json",
        "state (oct a | okta | octa)": "okta",
        "state (a w s | aws)": "aws",
        "state bite": "byte",
        "state bites": "bytes",
        "state state": "state",
    }
)
