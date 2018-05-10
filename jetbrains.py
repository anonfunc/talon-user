import urllib

from talon import applescript
from talon.api import ffi
from talon.voice import Key, press, Str, Context
from talon.ui import active_app

import requests

from user.utility import text, text_to_number, text_to_range, optional_numerals

# Each IDE gets its own port, as otherwise you wouldn't be able
# to run two at the same time and switch between them.
# Note that MPS and IntelliJ ultimate will conflict...
port_mapping = {
    "com.jetbrains.intellij": 8653,
    "com.jetbrains.intellij.ce": 8654,
    "com.jetbrains.AppCode": 8655,
    "com.jetbrains.CLion": 8657,
    "com.jetbrains.datagrip": 8664,
    "com.jetbrains.goland": 8659,
    "com.jetbrains.PhpStorm": 8662,
    "com.jetbrains.pycharm": 8658,
    "com.jetbrains.rubymine": 8661,
    "com.jetbrains.WebStorm": 8663,
    "com.google.android.studio": 8652,
}


def send_idea_command(cmd):
    print("Sending {}".format(cmd))
    bundle = active_app().bundle
    port = port_mapping.get(bundle, None)
    if port:
        response = requests.get("http://localhost:{}/{}".format(port, cmd))
        response.raise_for_status()
        return response.text


def idea(cmd):
    return lambda _: send_idea_command(cmd)


def idea_num(cmd, drop=1):

    def handler(m):
        line = text_to_number(m._words[drop:])
        print(cmd.format(line))
        send_idea_command(cmd.format(line))

    return handler


def idea_range(cmd, drop=1):

    def handler(m):
        start, end = text_to_range(m._words[drop:])
        print(cmd.format(start, end))
        send_idea_command(cmd.format(start, end))

    return handler


def idea_words(cmd, join=" "):

    def handler(m):
        args = [str(w) for w in m.dgndictation[0]._words]
        print(args)
        send_idea_command(cmd.format(join.join(args)))

    return handler


ctx = Context(
    "jetbrains", func=lambda app, _: any(app.bundle == b for b in port_mapping.keys())
)

keymap = {}
keymap.update(
    {
        "complete": idea("action CodeCompletion"),
        "smarter": idea("action SmartTypeCompletion"),
        "finish": idea("action EditorCompleteStatement"),
        "zoom": idea("action HideAllWindows"),
        "find (usage | usages)": idea("action FindUsages"),
        "(refactor | reflector) [<dgndictation>]": [
            idea("action Refactorings.QuickListPopupAction"), text
        ],
        "fix": idea("action ShowIntentionActions"),
        "fix next": [idea("action GotoNextError"), idea("action ShowIntentionActions")],
        "fix previous": [
            idea("action GotoPreviousError"), idea("action ShowIntentionActions")
        ],
        "find declaration": idea("action GotoDeclaration"),
        "find (implementers | implementations)": idea("action GotoImplementation"),
        "find type": idea("action GotoTypeDeclaration"),
        "(find previous | trail) [<dgndictation>]": idea_words("find prev {}"),
        "(find next | crew) [<dgndictation>]": idea_words("find next {}"),
        "find [<dgndictation>]": [idea("action SearchEverywhere"), text],
        "surround this [<dgndictation>]": [idea("action SurroundWith"), text],
        "generate code [<dgndictation>]": [idea("action Generate"), text],
        "template [<dgndictation>]": [idea("action InsertLiveTemplate"), text],
        "select less": idea("action EditorUnSelectWord"),
        "select more": idea("action EditorSelectWord"),
        "(select line | shackle)": [
            idea("action EditorLineStart"), idea("action EditorLineEndWithSelection")
        ],
        "select block": [
            idea("action EditorCodeBlockStart"),
            idea("action EditorCodeBlockEndWithSelection"),
        ],
        "select this line"
        + optional_numerals: [
            idea_num("goto {} 9999", drop=3),
            idea("action EditorLineStartWithSelection"),
        ],
        "select lines {} until {}".format(
            optional_numerals, optional_numerals
        ): idea_range(
            "range {} {}", drop=2
        ),
        "select until" + optional_numerals: idea_num("extend {}", drop=2),
        "select just"
        + optional_numerals: [
            idea_num("goto {} 0", drop=2), idea("action EditorLineEndWithSelection")
        ],
        "go to end of" + optional_numerals: idea_num("goto {} 9999", drop=4),
        "(clean | clear) line": [
            idea("action EditorLineEnd"), idea("action EditorDeleteToLineStart")
        ],
        "delete line": idea("action EditorDeleteLine"),
        "delete to end": idea("action EditorDeleteToLineEnd"),
        "delete to start": idea("action EditorDeleteToLineStart"),
        "drag up": idea("action MoveLineUp"),
        "drag down": idea("action MoveLineDown"),
        "duplicate": idea("action EditorDuplicate"),
        "go back": idea("action Back"),
        "go forward": idea("action Forward"),
        "(synchronizing | synchronize)": idea("action Synchronize"),
        "comment": idea("action CommentByLineComment"),
        "command [<dgndictation>]": [idea("action GotoAction"), text],
        "go to" + optional_numerals: idea_num("goto {} 0", drop=2),
        "clone" + optional_numerals: idea_num("clone {}"),
    }
)

ctx.keymap(keymap)
