import os
import time

import requests
import talon.clip as clip
from talon import ctrl
from talon.ui import active_app
from talon.voice import Context, Key

from ..misc.basic_keys import alphabet
from ..utils import optional_numerals, numerals, text, text_to_number, text_to_range

try:
    from ..text.homophones import all_homophones

    # Map from every homophone back to the row it was in.
    homophone_lookup = {
        item.lower(): words for canon, words in all_homophones.items() for item in words
    }
except ImportError:
    homophone_lookup = {"right": ["right", "write"], "write": ["right", "write"]}
    all_homophones = homophone_lookup.keys()

try:
    from ..misc.mouse import delayed_click
except ImportError:
    print("Fallback mouse click logic")

    def delayed_click():
        ctrl.mouse_click(button=0)


# Each IDE gets its own port, as otherwise you wouldn't be able
# to run two at the same time and switch between them.
# Note that MPS and IntelliJ ultimate will conflict...
port_mapping = {
    "com.jetbrains.intellij": 8653,
    "com.jetbrains.intellij-EAP": 8653,
    "com.jetbrains.intellij.ce": 8654,
    "com.jetbrains.AppCode": 8655,
    "com.jetbrains.CLion": 8657,
    "com.jetbrains.datagrip": 8664,
    "com.jetbrains.goland": 8659,
    "com.jetbrains.goland-EAP": 8659,
    "com.jetbrains.PhpStorm": 8662,
    "com.jetbrains.pycharm": 8658,
    "com.jetbrains.rider": 8660,
    "com.jetbrains.rubymine": 8661,
    "com.jetbrains.WebStorm": 8663,
    "com.google.android.studio": 8652,
}

extendCommands = []


def set_extend(*commands):
    def set_inner(_):
        global extendCommands
        extendCommands = commands

    return set_inner


def extend_action(_):
    global extendCommands
    for cmd in extendCommands:
        send_idea_command(cmd)


def _get_nonce(port):
    try:
        with open(os.path.join("/tmp", "vcidea_" + str(port)), "r") as fh:
            return fh.read()
    except IOError:
        return None


def send_idea_command(cmd):
    # print("Sending {}".format(cmd))
    bundle = active_app().bundle
    port = port_mapping.get(bundle, None)
    nonce = _get_nonce(port)
    if port and nonce:
        response = requests.get(
            "http://localhost:{}/{}/{}".format(port, nonce, cmd), timeout=(0.05, 3.05)
        )
        response.raise_for_status()
        return response.text


def get_idea_location():
    return send_idea_command("location").split()


def idea(*cmds):
    def inner(_):
        global extendCommands
        extendCommands = cmds
        for cmd in cmds:
            send_idea_command(cmd)

    return inner


def idea_num(cmd, drop=1, zero_okay=False):
    def handler(m):
        # noinspection PyProtectedMember
        line = text_to_number(m._words[drop:])
        # print(cmd.format(line))
        if int(line) == 0 and not zero_okay:
            print("Not sending, arg was 0")
            return

        send_idea_command(cmd.format(line))
        global extendCommands
        extendCommands = []

    return handler


def idea_range(cmd, drop=1):
    def handler(m):
        # noinspection PyProtectedMember
        start, end = text_to_range(m._words[drop:])
        # print(cmd.format(start, end))
        send_idea_command(cmd.format(start, end))
        global extendCommands
        extendCommands = []

    return handler


def idea_words(cmd, join=" "):
    def handler(m):
        # noinspection PyProtectedMember
        args = [str(w) for w in m.dgndictation[0]._words]
        # print(args)
        send_idea_command(cmd.format(join.join(args)))

    return handler


def idea_find(direction):
    def handler(m):
        # noinspection PyProtectedMember
        args = [str(w) for w in m.dgndictation[0]._words]
        search_string = " ".join(args)
        cmd = "find {} {}"
        if len(args) == 1:
            word = args[0]
            if word in homophone_lookup:
                search_string = "({})".format("|".join(homophone_lookup[word]))
        # print(args)
        send_idea_command(cmd.format(direction, search_string))
        global extendCommands
        extendCommands = [cmd.format(direction, search_string)]

    return handler


def idea_bounded(direction):
    def handler(m):
        # noinspection PyProtectedMember
        print("hello")
        keys = [alphabet[k] for k in m["jetbrains.alphabet"]]
        search_string = "%5Cb" + r"%5B^-_ .()%5D*?".join(keys)  # URL escaped Java regex! '\b' 'A[%-_.()]*?Z"
        cmd = "find {} {}"
        print(keys, search_string, cmd)
        send_idea_command(cmd.format(direction, search_string))
        global extendCommands
        extendCommands = [cmd.format(direction, search_string)]

    return handler


def grab_identifier(m):
    old_clip = clip.get()
    # noinspection PyProtectedMember
    times = text_to_number(m._words[1:])  # hardcoded prefix length?
    if not times:
        times = 1
    try:
        old_line, old_col = get_idea_location()
        delayed_click(m, button=0, times=2)
        for _ in range(times - 1):
            send_idea_command("action EditorSelectWord")
        send_idea_command("action EditorCopy")
        send_idea_command("goto {} {}".format(old_line, old_col))
        send_idea_command("action EditorPaste")
    finally:
        clip.set(old_clip)


def is_real_jetbrains_editor(app, window):
    if app.bundle not in port_mapping:
        return False
    # XXX Expose "does editor have focus" as plugin endpoint.
    # XXX Window title empty in full screen.
    return "[" in window.title or len(window.title) == 0


# group = ContextGroup("jetbrains")
ctx = Context("jetbrains", func=is_real_jetbrains_editor)  # , group=group)
ctx.vocab = ["docker", "GitHub", "refactor"]
ctx.vocab_remove = ["doctor", "Doctor"]
ctx.keymap(
    {
        # Misc verbs
        "complete": [idea("action CodeCompletion")],
        "complete <dgndictation>++ [over]": [idea("action CodeCompletion"), text],
        "smart": [idea("action SmartTypeCompletion"), text],
        "smart <dgndictation>++ [over]": [idea("action SmartTypeCompletion"), text],
        "finish": idea("action EditorCompleteStatement"),
        "toggle tools": idea("action HideAllWindows"),
        "drag up": idea("action MoveLineUp"),
        "drag down": idea("action MoveLineDown"),
        "clone": idea("action EditorDuplicate"),
        f"clone line {optional_numerals}": [idea_num("clone {}", drop=2)],
        f"grab {optional_numerals}": [grab_identifier, set_extend()],
        # "(synchronizing | synchronize)": idea("action Synchronize"),
        "(action | please) [<dgndictation>++]": [idea("action GotoAction"), text],
        "extend": extend_action,
        # Refactoring
        "refactor": idea("action Refactorings.QuickListPopupAction"),
        "refactor <dgndictation>++ [over]": [
            idea("action Refactorings.QuickListPopupAction"),
            text,
        ],
        "extract variable": idea("action IntroduceVariable"),
        "extract field": idea("action IntroduceField"),
        "extract constant": idea("action IntroduceConstant"),
        "extract parameter": idea("action IntroduceParameter"),
        "extract interface": idea("action ExtractInterface"),
        "extract method": idea("action ExtractMethod"),
        # Quick Fix / Intentions
        "fix this": idea("action ShowIntentionActions"),
        "fix this <dgndictation>++ [over]": [idea("action ShowIntentionActions"), text],
        "fix next error": [idea("action GotoNextError", "action ShowIntentionActions")],
        "fix previous error": [
            idea("action GotoPreviousError", "action ShowIntentionActions")
        ],
        f"fix line {numerals}": [
            idea_num("goto {} 0", drop=2),
            idea("action GotoNextError", "action ShowIntentionActions"),
        ],
        # Go: move the caret
        "(go declaration | follow)": idea("action GotoDeclaration"),
        "go implementation": idea("action GotoImplementation"),
        "go usage": idea("action FindUsages"),
        "go type": idea("action GotoTypeDeclaration"),
        "go next result": idea("action FindNext"),
        "go last result": idea("action FindPrevious"),
        f"go line end {numerals}": idea_num("goto {} 9999", drop=3),
        "go last <dgndictation>": [
            idea_find("prev"),
            Key("right"),
            set_extend(extendCommands + ["action EditorRight"]),
        ],
        "go next <dgndictation>": [
            idea_find("next"),
            Key("left"),
            set_extend(extendCommands + ["action EditorLeft"]),
        ],
        "go last bounded {jetbrains.alphabet}+": [
            idea_bounded("prev"),
            Key("right"),
        ],
        "go next bounded {jetbrains.alphabet}+": [
            idea_bounded("next"),
            Key("left"),
        ],
        "go back": idea("action Back"),
        "go forward": idea("action Forward"),
        f"go line start {numerals}": idea_num("goto {} 0", drop=3),
        f"go line end {numerals}": idea_num("goto {} 9999", drop=3),
        # This will put the cursor past the indentation
        f"go line {numerals}": [
            idea_num("goto {} 9999", drop=2),
            idea("action EditorLineEnd"),
            idea("action EditorLineStart"),
            set_extend(),
        ],
        # Select
        "select last <dgndictation>": [
            idea_find("prev"),
        ],
        "select next <dgndictation>": [
            idea_find("next"),
        ],
        "select last bounded {jetbrains.alphabet}+": [
            idea_bounded("prev"),
        ],
        "select next bounded {jetbrains.alphabet}+": [
            idea_bounded("next"),
        ],
        "select last": idea("action EditorUnSelectWord"),
        "select this": idea("action EditorSelectWord"),
        "select line": [
            idea("action EditorLineStart", "action EditorLineEndWithSelection"),
            set_extend(
                "action EditorLineStart",
                "action EditorLineStart",
                "action EditorLineEndWithSelection",
            ),
        ],
        f"select line {numerals}": [
            idea_num("goto {} 0", drop=2),
            idea("action EditorLineStart", "action EditorLineEndWithSelection"),
            set_extend(
                "action EditorLineStart",
                "action EditorLineStart",
                "action EditorLineEndWithSelection",
            ),
        ],
        f"select lines {numerals} until {numerals}": idea_range("range {} {}", drop=2),
        f"select until line {numerals}": idea_num("extend {}", drop=3),
        # Search
        "search everywhere": idea("action SearchEverywhere"),
        "search everywhere <dgndictation>++ [over]": [
            idea("action SearchEverywhere"),
            text,
            set_extend(),
        ],
        "search recent": [idea("action RecentFiles"), set_extend()],
        "search recent <dgndictation>++ [over]": [
            idea("action RecentFiles"),
            text,
            set_extend(),
        ],
        "search": idea("action Find"),
        "search <dgndictation>++ [over]": [idea("action Find"), text],
        "search this": idea("action FindWordAtCaret"),
        # Templates: surround, generate, template.
        "surround [this]": idea("action SurroundWith"),
        "surround [this] <dgndictation>++ [over]": [idea("action SurroundWith"), text],
        "generate": idea("action Generate"),
        "generate <dgndictation>++ [over]": [idea("action Generate"), text],
        "template": idea("action InsertLiveTemplate"),
        "template <dgndictation>++ [over]": [idea("action InsertLiveTemplate"), text],
        "create template": idea("action SaveAsTemplate"),
        # Lines / Selections
        "clear line": [idea("action EditorLineEnd", "action EditorDeleteToLineStart")],
        f"clear line {numerals}": [
            idea_num("goto {} 0", drop=2),
            idea("action EditorLineEnd"),
            idea("action EditorDeleteToLineStart"),
        ],
        "clear this": [idea("action EditorSelectWord"), idea("action EditorDelete")],
        "clear last <dgndictation>": [
            idea_find("prev"),
            idea("action EditorDelete"),
            set_extend(extendCommands + ["action EditorDelete"]),
        ],
        "clear next <dgndictation>": [
            idea_find("next"),
            idea("action EditorDelete"),
            set_extend(extendCommands + ["action EditorDelete"]),
        ],
        "clear last bounded {jetbrains.alphabet}+": [
            idea_bounded("prev"),
            idea("action EditorDelete"),
            set_extend(extendCommands + ["action EditorDelete"]),
        ],
        "clear next bounded {jetbrains.alphabet}+": [
            idea_bounded("next"),
            idea("action EditorDelete"),
            set_extend(extendCommands + ["action EditorDelete"]),
        ],
        "clear line end": idea("action EditorDeleteToLineEnd"),
        "clear line start": idea("action EditorDeleteToLineStart"),
        f"clear lines {numerals} until {numerals}": [
            idea_range("range {} {}", drop=2),
            idea("action EditorDelete"),
        ],
        f"clear until line{numerals}": [
            idea_num("extend {}", drop=3),
            idea("action EditorDelete"),
        ],
        # Commenting
        "comment [(this | line)]": idea("action CommentByLineComment"),
        f"comment line {numerals}": [
            idea_num("goto {} 0", drop=2),
            idea("action EditorLineEnd"),
            idea("action CommentByLineComment"),
        ],
        "comment last <dgndictation>": [
            idea_find("prev"),
            idea("action EditorLineStart"),
            idea("action CommentByLineComment"),
        ],
        "comment next <dgndictation>": [
            idea_find("next"),
            idea("action EditorLineStart"),
            idea("action CommentByLineComment"),
        ],
        "comment last bounded {jetbrains.alphabet}+": [
            idea_bounded("prev"),
            idea("action EditorLineStart"),
            idea("action CommentByLineComment"),
        ],
        "comment next bounded {jetbrains.alphabet}+": [
            idea_bounded("next"),
            idea("action EditorLineStart"),
            idea("action CommentByLineComment"),
        ],
        "comment line end": [
            idea("action EditorLineEndWithSelection"),
            idea("action CommentByLineComment"),
        ],
        f"comment lines {numerals} until {numerals}": [
            idea_range("range {} {}", drop=2),
            idea("action CommentByLineComment"),
        ],
        f"comment until line {numerals}": [
            idea_num("extend {}", drop=3),
            idea("action CommentByLineComment"),
        ],
        # Recording
        "toggle recording": idea("action StartStopMacroRecording"),
        "edit (recording | recordings)": idea("action EditMacros"),
        "play recording": idea("action PlaybackLastMacro"),
        "play recording <dgndictation>": [
            idea("action PlaySavedMacrosAction"),
            text,
            Key("enter"),
        ],
        # Marks
        "go mark": idea("action ShowBookmarks"),
        "toggle mark": idea("action ToggleBookmark"),
        "go next mark": idea("action GotoNextBookmark"),
        "go last mark": idea("action GotoPreviousBookmark"),
        f"toggle mark (0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9)": idea_num(
            "action ToggleBookmark{}", drop=1, zero_okay=True
        ),
        f"go mark (0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9)": idea_num(
            "action GotoBookmark{}", drop=2, zero_okay=True
        ),
        # Splits
        "split vertically": idea("action SplitVertically"),
        "split horizontally": idea("action SplitHorizontally"),
        "split flip": idea("action ChangeSplitOrientation"),
        "clear split": idea("action Unsplit"),
        "clear all splits": idea("action UnsplitAll"),
        "go next split": idea("action NextSplitter"),
        "go last split": idea("action LastSplitter"),
        # Clipboard
        # "clippings": idea("action PasteMultiple"),  # XXX Might be a long-lived action.  Replaced with Alfred.
        "copy path": idea("action CopyPaths"),
        "copy reference": idea("action CopyReference"),
        "copy pretty": idea("action CopyAsRichText"),
        # File Creation
        "create sibling": idea("action NewElementSamePlace"),
        "create sibling <dgndictation>++ [over]": [
            idea("action NewElementSamePlace"),
            text,
        ],
        "create file": idea("action NewElement"),
        "create file <dgndictation>++ [over]": [idea("action NewElement"), text],
        # Task Management
        "select task": [idea("action tasks.goto")],
        "go browser task": [idea("action tasks.open.in.browser")],
        "switch task": [idea("action tasks.switch")],
        "clear task": [idea("action tasks.close")],
        "fix task settings": [idea("action tasks.configure.servers")],
        # Git / Github (not using verb-noun-adjective pattern, mirroring terminal commands.)
        "jet pull": idea("action Vcs.UpdateProject"),
        "jet commit": idea("action CheckinProject"),
        "jet log": idea("action Vcs.ShowTabbedFileHistory"),
        "jet browse": idea("action Github.Open.In.Browser"),
        "jet (gets | gist)": idea("action Github.Create.Gist"),
        "jet (pull request | request)": idea("action Github.Create.Pull.Request"),
        "jet (view | show | list) (requests | request)": idea(
            "action Github.View.Pull.Request"
        ),
        "jet (annotate | blame)": idea("action Annotate"),
        "jet": idea("action Vcs.QuickListPopupAction"),
    }
)
ctx.set_list("alphabet", alphabet.keys())

# group.load()
