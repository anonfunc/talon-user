import requests
import talon.clip as clip
from talon import ctrl, tap
from talon.ui import active_app
from talon.voice import Context
from user.utility import optional_numerals, text, text_to_number, text_to_range

from user.mouse import delayed_click


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
        response = requests.get("http://localhost:{}/{}".format(port, cmd), timeout=(0.05, 3.05))
        response.raise_for_status()
        return response.text


def get_idea_location():
    return send_idea_command("location").split()


def idea(cmd):
    return lambda _: send_idea_command(cmd)


def idea_num(cmd, drop=1):

    def handler(m):
        line = text_to_number(m._words[drop:])
        print(cmd.format(line))
        if int(line) == 0:
            print("Not sending, arg was 0")
            return
        
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


def grab_identifier(m):
    old_clip = clip.get()
    times = text_to_number(m._words[1:])  # hardcoded prefix length?
    if not times:
        times = 1
    try:
        old_line, old_col = get_idea_location()
        delayed_click(m, button=0, times=2)
        for _ in range(times):
            send_idea_command("action EditorSelectWord")
        send_idea_command("action EditorCopy")
        send_idea_command("goto {} {}".format(old_line, old_col))
        send_idea_command("action EditorPaste")
    finally:
        clip.set(old_clip)

def _window_title():
    return ffi.string(
        applescript.run(
            'tell application "System Events" to get title of first window of (first application process whose frontmost is true)'
        )
    ).decode("utf-8")

def _window_role():
    return ffi.string(
        applescript.run(
            'tell application "System Events" to get subrole of first window of (first application process whose frontmost is true)'
        )
    ).decode("utf-8")   

def is_real_jetbrains_editor(app, _):
    if not any(app.bundle == b for b in port_mapping.keys()):
        return False
    # XXX Expose "does editor have focus" as plugin endpoint.

    # We only want to use IntelliJ package if we're looking at the editor window
    # Dialogs should use basic handling.
    # Most dialogs have no title, but some do.
    windowTitle = _window_title()
    windowRole = _window_role()
    # However, the main editor windows always have a title like: 
    #   name [path] - file/path
    # Using the square bracket as a heuristic should do for now.

    if windowRole != "AXStandardWindow":
        # Can't differentiate between command pallet and completion dialogues
        # Still should prevent sending editor commands.
        return False
    # False for modal dialogs.
    return windowTitle and '[' in windowTitle


ctx = Context("jetbrains", func=is_real_jetbrains_editor)

keymap = {}
keymap.update(
    {
        "complete": idea("action CodeCompletion"),
        "smarter": idea("action SmartTypeCompletion"),
        "finish": idea("action EditorCompleteStatement"),
        "zoom": idea("action HideAllWindows"),
        "find (usage | usages)": idea("action FindUsages"),
        "(refactor | reflector) [<dgndictation>]": [
            idea("action Refactorings.QuickListPopupAction"),
            text,
        ],
        "fix [this]": idea("action ShowIntentionActions"),
        "fix next [error]": [
            idea("action GotoNextError"),
            idea("action ShowIntentionActions"),
        ],
        "fix previous [error]": [
            idea("action GotoPreviousError"),
            idea("action ShowIntentionActions"),
        ],
        "visit declaration": idea("action GotoDeclaration"),
        "visit (implementers | implementations)": idea("action GotoImplementation"),
        "visit type": idea("action GotoTypeDeclaration"),
        "(select previous | trail) [<dgndictation>]": idea_words("find prev {}"),
        "(select next | crew) [<dgndictation>]": idea_words("find next {}"),
        "search everywhere [for] [<dgndictation>]": [idea("action SearchEverywhere"), text],
        "find [<dgndictation>]": [idea("action Find"), text],
        "find this": idea("action FindWordAtCaret"),
        "next": idea("action FindNext"),
        "last": idea("action FindPrevious"),
        "surround [this] [<dgndictation>]": [idea("action SurroundWith"), text],
        "generate [<dgndictation>]": [idea("action Generate"), text],
        "template [<dgndictation>]": [idea("action InsertLiveTemplate"), text],
        "select less": idea("action EditorUnSelectWord"),
        "select more": idea("action EditorSelectWord"),
        "select line"
        + optional_numerals: [
            idea_num("goto {} 0", drop=2),
            idea("action EditorLineStart"),
            idea("action EditorLineEndWithSelection"),
        ],
        "select block": [
            idea("action EditorCodeBlockStart"),
            idea("action EditorCodeBlockEndWithSelection"),
        ],
        "select this line": [
            idea("action EditorLineStart"),
            idea("action EditorLineEndWithSelection"),
        ],
        "select lines {} until {}".format(
            optional_numerals, optional_numerals
        ): idea_range("range {} {}", drop=2),
        "select until" + optional_numerals: idea_num("extend {}", drop=2),
        "select just"
        + optional_numerals: [
            idea_num("goto {} 9999", drop=2),
            idea("action EditorLineStartWithSelection"),
        ],
        "go to end of" + optional_numerals: idea_num("goto {} 9999", drop=4),
        "(clean | clear) line": [
            idea("action EditorLineEnd"),
            idea("action EditorDeleteToLineStart"),
        ],
        "delete line": idea("action EditorDeleteLine"),  # xxx optional line number
        "delete to end": idea("action EditorDeleteToLineEnd"),
        "delete to start": idea("action EditorDeleteToLineStart"),
        "drag up": idea("action MoveLineUp"),
        "drag down": idea("action MoveLineDown"),
        "duplicate": idea("action EditorDuplicate"),
        "go back": idea("action Back"),
        "go forward": idea("action Forward"),
        "(synchronizing | synchronize)": idea("action Synchronize"),
        "comment": idea("action CommentByLineComment"),
        "action [<dgndictation>]": [idea("action GotoAction"), text],
        "(go to | jump to)" + optional_numerals: idea_num("goto {} 0", drop=2),
        "clone line" + optional_numerals: idea_num("clone {}", drop=2),
        "fix this": idea("action ShowIntentionActions"),
        "fix next": [idea("action GotoNextError"), idea("action ShowIntentionActions")],
        "fix previous": [
            idea("action GotoPreviousError"),
            idea("action ShowIntentionActions"),
        ],
        "grab" + optional_numerals: grab_identifier,
    }
)

ctx.keymap(keymap)
