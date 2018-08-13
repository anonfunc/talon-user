import os

import requests
import talon.clip as clip
from talon import ctrl
from talon.ui import active_app
from talon.voice import Context, ContextGroup, Key
from user.std import text, parse_word

try:
    from user.mouse import delayed_click
except ImportError:

    def delayed_click():
        ctrl.mouse_click(button=0)


# region Supporting Code
_numeral_map = dict((str(n), n) for n in range(0, 20))
for n in range(20, 101, 10):
    _numeral_map[str(n)] = n
for n in range(100, 1001, 100):
    _numeral_map[str(n)] = n
for n in range(1000, 10001, 1000):
    _numeral_map[str(n)] = n
_numeral_map["oh"] = 0  # synonym for zero
_numeral_map["and"] = None  # drop me
_numerals = " (" + " | ".join(sorted(_numeral_map.keys())) + ")+"
_optional_numerals = " (" + " | ".join(sorted(_numeral_map.keys())) + ")*"


def text_to_number(words):
    tmp = [str(s).lower() for s in words]
    words = [parse_word(word) for word in tmp]

    result = 0
    factor = 1
    for word in reversed(words):
        print("{} {} {}".format(result, factor, word))
        if word not in _numerals:
            raise Exception("not a number: {}".format(words))

        number = _numeral_map[word]
        if number is None:
            continue

        number = int(number)
        if number > 10:
            result = result + number
        else:
            result = result + factor * number
        factor = (10 ** len(str(number))) * factor
    return result


def text_to_range(words, delimiter="until"):
    tmp = [str(s).lower() for s in words]
    split = tmp.index(delimiter)
    start = text_to_number(words[:split])
    end = text_to_number(words[split + 1 :])
    return start, end


# endregion

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
    "com.jetbrains.rider": 8660,
    "com.jetbrains.rubymine": 8661,
    "com.jetbrains.WebStorm": 8663,
    "com.google.android.studio": 8652,
}


def _get_nonce(port):
    try:
        with open(os.path.join("/tmp", "vcidea_" + str(port)), "r") as fh:
            return fh.read()
    except IOError:
        return None


def send_idea_command(cmd):
    print("Sending {}".format(cmd))
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


def is_real_jetbrains_editor(app, window):
    if app.bundle not in port_mapping:
        return False
    # XXX Expose "does editor have focus" as plugin endpoint.
    # XXX Window title empty in full screen.
    return "[" in window.title or len(window.title) == 0


# group = ContextGroup("jetbrains")
ctx = Context("jetbrains", func=is_real_jetbrains_editor)  # , group=group)

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
        "search everywhere [for] [<dgndictation>]": [
            idea("action SearchEverywhere"),
            text,
        ],
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
        + _optional_numerals: [
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
            _optional_numerals, _optional_numerals
        ): idea_range("range {} {}", drop=2),
        "select until" + _optional_numerals: idea_num("extend {}", drop=2),
        "(go | jump) to end of" + _optional_numerals: idea_num("goto {} 9999", drop=4),
        "(clean | clear) line": [
            idea("action EditorLineEnd"),
            idea("action EditorDeleteToLineStart"),
        ],
        "(delete | remove) line": idea(
            "action EditorDeleteLine"
        ),  # xxx optional line number
        "(delete | clear) to end": idea("action EditorDeleteToLineEnd"),
        "(delete | clear) to start": idea("action EditorDeleteToLineStart"),
        "drag up": idea("action MoveLineUp"),
        "drag down": idea("action MoveLineDown"),
        "duplicate": idea("action EditorDuplicate"),
        "(go | jump) back": idea("action Back"),
        "(go | jump) forward": idea("action Forward"),
        "(synchronizing | synchronize)": idea("action Synchronize"),
        "comment": idea("action CommentByLineComment"),
        "(action | please) [<dgndictation>]": [idea("action GotoAction"), text],
        "(go to | jump to)" + _optional_numerals: idea_num("goto {} 0", drop=2),
        "clone line" + _optional_numerals: idea_num("clone {}", drop=2),
        "fix this": idea("action ShowIntentionActions"),
        "fix next": [idea("action GotoNextError"), idea("action ShowIntentionActions")],
        "fix previous": [
            idea("action GotoPreviousError"),
            idea("action ShowIntentionActions"),
        ],
        "grab" + _optional_numerals: grab_identifier,
        "(start | stop) recording": idea("action StartStopMacroRecording"),
        "edit (recording | recordings)": idea("action EditMacros"),
        "play recording": idea("action PlaybackLastMacro"),
        "play recording <dgndictation>": [
            idea("action PlaySavedMacrosAction"),
            text,
            Key("enter"),
        ],
    }
)

ctx.keymap(keymap)
# group.load()
