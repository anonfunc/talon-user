import os
import time

import requests
import talon.clip as clip
from talon import ctrl
from talon.ui import active_app
from talon.voice import Context, Key

from ..misc.basic_keys import alphabet
from .. import utils

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

    def delayed_click(_, button=0, times=1, from_end=False, mods=None):
        ctrl.mouse_click(button=button)


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
toHereCommands = []
old_line, old_col = 0, 0


def set_extend(*commands):
    def set_inner(_):
        global extendCommands
        extendCommands = commands

    return set_inner


def extend_action(m):
    global extendCommands
    # noinspection PyProtectedMember
    count = max(utils.text_to_number([utils.parse_word(w) for w in m._words[1:]]), 1)
    for _ in range(count):
        for cmd in extendCommands:
            send_idea_command(cmd)


def set_to_here(*commands):
    global toHereCommands, old_line, old_col
    old_line, old_col = get_idea_location()
    toHereCommands = commands


def to_here(m):
    global toHereCommands
    for cmd in toHereCommands:
        cmd(m)
    toHereCommands = []


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
    def inner(m):
        global extendCommands
        extendCommands = cmds
        for cmd in cmds:
            send_idea_command(cmd)

    return inner


def idea_num(cmd, drop=1, zero_okay=False):
    def handler(m):
        # noinspection PyProtectedMember
        line = utils.text_to_number(m._words[drop:])
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
        start, end = utils.text_to_range(m._words[drop:])
        # print(cmd.format(start, end))
        send_idea_command(cmd.format(start, end))
        global extendCommands
        extendCommands = []

    return handler


def idea_find(direction):
    def handler(m):
        # noinspection PyProtectedMember
        args = utils.parse_words(m)
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
        search_string = "%5Cb" + r"%5B^-_ .()%5D*?".join(
            keys
        )  # URL escaped Java regex! '\b' 'A[%-_.()]*?Z"
        cmd = "find {} {}"
        print(keys, search_string, cmd)
        send_idea_command(cmd.format(direction, search_string))
        global extendCommands
        extendCommands = [cmd.format(direction, search_string)]

    return handler


def grab_identifier(m):
    old_clip = clip.get()
    # noinspection PyProtectedMember
    times = utils.text_to_number(m._words[1:])  # hardcoded prefix length?
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
        "perfect": [
            idea("action CodeCompletion", "action CodeCompletion")
        ],  # perfect == extra complete
        "smart": [idea("action SmartTypeCompletion")],
        # Variants which take text?  Replaced mostly with "call" formatter.
        # "complete <dgndictation>++ [over]": [idea("action CodeCompletion"), text],
        # "smart <dgndictation>++ [over]": [idea("action SmartTypeCompletion"), text],
        "finish": idea("action EditorCompleteStatement"),
        "toggle tools": idea("action HideAllWindows"),
        "drag up": idea("action MoveLineUp"),
        "drag down": idea("action MoveLineDown"),
        "clone this": idea("action EditorDuplicate"),
        "clone line": idea("action EditorDuplicate"),
        f"clone line {utils.numerals}": [idea_num("clone {}", drop=2)],
        f"grab {utils.optional_numerals}": [grab_identifier, set_extend()],
        # "(synchronizing | synchronize)": idea("action Synchronize"),
        "(action | please) [<dgndictation>++]": [idea("action GotoAction"), utils.text],
        f"extend {utils.optional_numerals}": extend_action,
        "to here": to_here,
        # Refactoring
        "refactor": idea("action Refactorings.QuickListPopupAction"),
        "refactor <dgndictation>++ [over]": [
            idea("action Refactorings.QuickListPopupAction"),
            utils.text,
        ],
        "extract variable": idea("action IntroduceVariable"),
        "extract field": idea("action IntroduceField"),
        "extract constant": idea("action IntroduceConstant"),
        "extract parameter": idea("action IntroduceParameter"),
        "extract interface": idea("action ExtractInterface"),
        "extract method": idea("action ExtractMethod"),
        # Quick Fix / Intentions
        "fix this": idea("action ShowIntentionActions"),
        "fix this <dgndictation>++ [over]": [
            idea("action ShowIntentionActions"),
            utils.text,
        ],
        "fix next error": [idea("action GotoNextError", "action ShowIntentionActions")],
        "fix last error": [
            idea("action GotoPreviousError", "action ShowIntentionActions")
        ],
        f"fix line {utils.numerals}": [
            idea_num("goto {} 0", drop=2),
            idea("action GotoNextError", "action ShowIntentionActions"),
        ],
        "fix (format | formatting)": idea("action ReformatCode"),
        # Go: move the caret
        "(go declaration | follow)": idea("action GotoDeclaration"),
        "go implementation": idea("action GotoImplementation"),
        "go usage": idea("action FindUsages"),
        "go type": idea("action GotoTypeDeclaration"),
        "go next result": idea("action FindNext"),
        "go last result": idea("action FindPrevious"),
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
        "go last bounded {jetbrains.alphabet}+": [idea_bounded("prev"), Key("right")],
        "go next bounded {jetbrains.alphabet}+": [idea_bounded("next"), Key("left")],
        "go back": idea("action Back"),
        "go [to] here": [lambda m: delayed_click(m, from_end=True)],
        "go forward": idea("action Forward"),
        f"go line start {utils.numerals}": idea_num("goto {} 0", drop=3),
        f"go line end {utils.numerals}": idea_num("goto {} 9999", drop=3),
        # This will put the cursor past the indentation
        f"go line {utils.numerals}": [
            idea_num("goto {} 9999", drop=2),
            idea("action EditorLineEnd"),
            idea("action EditorLineStart"),
            set_extend(),
        ],
        # Select
        "select here": [
            lambda m: delayed_click(m, from_end=True),
            idea("action EditorLineStart", "action EditorLineEndWithSelection"),
        ],
        "select to here": [lambda m: delayed_click(m, from_end=True, mods=["shift"])],
        "select from here": lambda m: set_to_here(
            lambda _: delayed_click(m, from_end=True),
            lambda m2: delayed_click(m2, from_end=True, mods=["shift"]),
        ),
        "(correct | select phrase)": utils.select_last_insert,  # Nothing fancy for now.
        "select last <dgndictation>": [idea_find("prev")],
        "select next <dgndictation>": [idea_find("next")],
        "select last bounded {jetbrains.alphabet}+": [idea_bounded("prev")],
        "select next bounded {jetbrains.alphabet}+": [idea_bounded("next")],
        "select less": idea("action EditorUnSelectWord"),
        "select more": idea("action EditorSelectWord"),
        "select this": idea("action EditorSelectWord"),
        "multi-select up": idea("action EditorCloneCaretAbove"),
        "multi-select down": idea("action EditorCloneCaretBelow"),
        "multi-select fewer": idea("action UnselectPreviousOccurrence"),
        "multi-select more": idea("action SelectNextOccurrence"),
        "multi-select all": idea("action SelectAllOccurrences"),
        "select line": [
            idea("action EditorLineStart", "action EditorLineEndWithSelection"),
            set_extend(
                "action EditorLineStart",
                "action EditorLineStart",
                "action EditorLineEndWithSelection",
            ),
        ],
        f"select line {utils.numerals}": [
            idea_num("goto {} 0", drop=2),
            idea("action EditorLineStart", "action EditorLineEndWithSelection"),
            set_extend(
                "action EditorLineStart",
                "action EditorLineStart",
                "action EditorLineEndWithSelection",
            ),
        ],
        f"select lines {utils.numerals} until {utils.numerals}": idea_range(
            "range {} {}", drop=2
        ),
        f"select until line {utils.numerals}": idea_num("extend {}", drop=3),
        # Search
        "search everywhere": idea("action SearchEverywhere"),
        "search everywhere <dgndictation>++ [over]": [
            idea("action SearchEverywhere"),
            utils.text,
            set_extend(),
        ],
        "search recent": [idea("action RecentFiles"), set_extend()],
        "search recent <dgndictation>++ [over]": [
            idea("action RecentFiles"),
            utils.text,
            set_extend(),
        ],
        "search": idea("action Find"),
        "search <dgndictation> [over]": [idea("action Find"), utils.text],
        "search in path": idea("action FindInPath"),
        "search in path <dgndictation> [over]": [idea("action FindInPath"), utils.text],
        "search this": idea("action FindWordAtCaret"),
        # Templates: surround, generate, template.
        "surround [this]": idea("action SurroundWith"),
        "surround [this] <dgndictation>++ [over]": [
            idea("action SurroundWith"),
            utils.text,
        ],
        "generate": idea("action Generate"),
        "generate <dgndictation>++ [over]": [idea("action Generate"), utils.text],
        "template": idea("action InsertLiveTemplate"),
        "template <dgndictation>++ [over]": [
            idea("action InsertLiveTemplate"),
            utils.text,
        ],
        "create template": idea("action SaveAsTemplate"),
        # Lines / Selections
        "clear line": [idea("action EditorLineEnd", "action EditorDeleteToLineStart")],
        f"clear line {utils.numerals}": [
            idea_num("goto {} 0", drop=2),
            idea("action EditorLineEnd"),
            idea("action EditorDeleteToLineStart"),
        ],
        "clear here": [
            lambda m: delayed_click(m, from_end=True),
            idea("action EditorLineStart", "action EditorDelete"),
        ],
        "clear to here": [
            lambda m: delayed_click(m, from_end=True, mods=["shift"]),
            idea("action EditorDelete"),
        ],
        "clear from here": [
            (
                lambda m: set_to_here(
                    lambda _: delayed_click(m, from_end=True),
                    lambda m2: delayed_click(m2, from_end=True, mods=["shift"]),
                    lambda _: time.sleep(0.2),
                    idea("action EditorDelete"),
                )
            )
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
        f"clear lines {utils.numerals} until {utils.numerals}": [
            idea_range("range {} {}", drop=2),
            idea("action EditorDelete"),
        ],
        f"clear until line {utils.numerals}": [
            idea_num("extend {}", drop=3),
            idea("action EditorDelete"),
        ],
        # Commenting
        "comment line": idea("action CommentByLineComment"),
        "comment here": [
            lambda m: delayed_click(m, from_end=True),
            idea("action EditorLineStart", "action CommentByLineComment"),
        ],
        "comment to here": [
            lambda m: delayed_click(m, from_end=True, mods=["shift"]),
            idea("action CommentByLineComment"),
        ],
        "comment from here": lambda m: set_to_here(
            lambda _: delayed_click(m, from_end=True),
            lambda m2: delayed_click(m2, from_end=True, mods=["shift"]),
            lambda _: time.sleep(0.2),
            idea("action CommentByLineComment"),
        ),
        f"comment line {utils.numerals}": [
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
        f"comment lines {utils.numerals} until {utils.numerals}": [
            idea_range("range {} {}", drop=2),
            idea("action CommentByLineComment"),
        ],
        f"comment until line {utils.numerals}": [
            idea_num("extend {}", drop=3),
            idea("action CommentByLineComment"),
        ],
        # Recording
        "toggle recording": idea("action StartStopMacroRecording"),
        "edit (recording | recordings)": idea("action EditMacros"),
        "play recording": idea("action PlaybackLastMacro"),
        "play recording <dgndictation>": [
            idea("action PlaySavedMacrosAction"),
            utils.text,
            Key("enter"),
        ],
        # Marks
        "go mark": idea("action ShowBookmarks"),
        "toggle mark": idea("action ToggleBookmark"),
        "toggle mark here": [
            lambda m: delayed_click(m, from_end=True),
            idea("action ToggleBookmark"),
        ],
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
            utils.text,
        ],
        "create file": idea("action NewElement"),
        "create file <dgndictation>++ [over]": [idea("action NewElement"), utils.text],
        # Task Management
        "go task": [idea("action tasks.goto")],
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
        # Tool windows:
        # Toggling various tool windows
        "toggle project": idea("action ActivateProjectToolWindow"),
        "toggle find": idea("action ActivateFindToolWindow"),
        "toggle run": idea("action ActivateRunToolWindow"),
        "toggle debug": idea("action ActivateDebugToolWindow"),
        "toggle events": idea("action ActivateEventLogToolWindow"),
        "toggle terminal": idea("action ActivateTerminalToolWindow"),
        "toggle jet": idea("action ActivateVersionControlToolWindow"),
        "toggle structure": idea("action ActivateStructureToolWindow"),
        "toggle database": idea("action ActivateDatabaseToolWindow"),
        "toggle database changes": idea("action ActivateDatabaseChangesToolWindow"),
        "toggle make": idea("action ActivatemakeToolWindow"),
        "toggle to do": idea("action ActivateTODOToolWindow"),
        "toggle docker": idea("action ActivateDockerToolWindow"),
        "toggle favorites": idea("action ActivateFavoritesToolWindow"),
        "toggle last": idea("action JumpToLastWindow"),
        # Pin/dock/float
        "toggle pinned": idea("action TogglePinnedMode"),
        "toggle docked": idea("action ToggleDockMode"),
        "toggle floating": idea("action ToggleFloatingMode"),
        "toggle windowed": idea("action ToggleWindowedMode"),
        "toggle split": idea("action ToggleSideMode"),
        # Grow / Shrink
        "(grow | shrink) window right": idea("action ResizeToolWindowRight"),
        "(grow | shrink) window left": idea("action ResizeToolWindowLeft"),
        "(grow | shrink) window up": idea("action ResizeToolWindowUp"),
        "(grow | shrink) window down": idea("action ResizeToolWindowDown"),
        # Matching generic editor interface as well.
        # moving
        "go word left": idea("action EditorPreviousWord"),
        "go word right": idea("action EditorNextWord"),
        "go camel left": idea("action EditorPreviousWordInDifferentHumpsMode"),
        "go camel right": idea("action EditorNextWordInDifferentHumpsMode"),
        "go line start": idea("action EditorLineStart"),
        "go line end": idea("action EditorLineEnd"),
        "go way left": idea("action EditorLineStart"),
        "go way right": idea("action EditorLineEnd"),
        "go way down": idea("action EditorTextEnd"),
        "go way up": idea("action EditorTextStart"),
        # selecting
        "select all": idea("action $SelectAll"),
        "select left": idea("action EditorLeftWithSelection"),
        "select right": idea("action EditorRightWithSelection"),
        "select up": idea("action EditorUpWithSelection"),
        "select down": idea("action EditorDownWithSelection"),
        "select word left": idea("action EditorPreviousWordWithSelection"),
        "select word right": idea("action EditorNextWordWithSelection"),
        "select camel left": idea(
            "action EditorPreviousWordInDifferentHumpsModeWithSelection"
        ),
        "select camel right": idea(
            "action EditorNextWordInDifferentHumpsModeWithSelection"
        ),
        "select way left": idea("action EditorLineStartWithSelection"),
        "select way right": idea("action EditorLineEndWithSelection"),
        "select way up": idea("action EditorTextStartWithSelection"),
        "select way down": idea("action EditorTextEndWithSelection"),
        # deleting
        "clear left": idea("action EditorBackSpace"),
        "clear right": idea("action EditorDelete"),
        "clear up": idea("action EditorUpWithSelection", "action EditorBackSpace"),
        "clear down": idea("action EditorDownWithSelection", "action EditorBackSpace"),
        "clear word left": idea(
            "action EditorPreviousWordWithSelection", "action EditorBackSpace"
        ),
        "clear word right": idea(
            "action EditorNextWordWithSelection", "action EditorBackSpace"
        ),
        "clear camel left": idea(
            "action EditorPreviousWordInDifferentHumpsModeWithSelection",
            "action EditorBackSpace",
        ),
        "clear camel right": idea(
            "action EditorNextWordInDifferentHumpsModeWithSelection",
            "action EditorBackSpace",
        ),
        "clear way left": idea("action EditorDeleteToLineStart"),
        "clear way right": idea("action EditorDeleteToLineEnd"),
        "clear way up": idea(
            "action EditorTextStartWithSelection", "action EditorBackSpace"
        ),
        "clear way down": idea(
            "action EditorTextEndWithSelection", "action EditorBackSpace"
        ),
    }
)
ctx.set_list("alphabet", alphabet.keys())

# group.load()
