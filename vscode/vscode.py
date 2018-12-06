import os
import json
import time
import threading

import requests
import talon.clip as clip
from talon import ctrl
from talon.ui import active_app
from talon.voice import Context, ContextGroup, Key, Str

try:
    from user.mouse import delayed_click
except ImportError:

    def delayed_click():
        ctrl.mouse_click(button=0)


# region Supporting Code
mapping = {"semicolon": ";", "new-line": "\n", "new-paragraph": "\n\n"}
punctuation = set(".,-!?")


def parse_word(word):
    word = str(word).lstrip("\\").split("\\", 1)[0]
    word = mapping.get(word, word)
    return word


def join_words(words, sep=" "):
    out = ""
    for i, word in enumerate(words):
        if i > 0 and word not in punctuation:
            out += sep
        out += word
    return out

def parse_words(m):
    try:
        return list(map(parse_word, m.dgndictation[0]._words))
    except AttributeError:
        return []


def insert(s):
    Str(s)(None)


def text(m):
    insert(join_words(parse_words(m)).lower())



_numeral_map = dict((str(n), n) for n in range(0, 20))
for n in range(20, 101, 10):
    _numeral_map[str(n)] = n
for n in range(100, 1001, 100):
    _numeral_map[str(n)] = n
for n in range(1000, 10001, 1000):
    _numeral_map[str(n)] = n
_numeral_map["oh"] = 0  # synonym for zero
_numeral_map["and"] = None  # drop me
_numerals = "(" + " | ".join(sorted(_numeral_map.keys())) + ")+"
_optional_numerals = "(" + " | ".join(sorted(_numeral_map.keys())) + ")*"


def text_to_number(words):
    tmp = [str(s).lower() for s in words]
    words = [parse_word(word) for word in tmp]

    result = 0
    factor = 1
    for word in reversed(words):
        print("{} {} {}".format(result, factor, word))
        if word not in _numeral_map:
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


def delay(amount=0.1):
    return lambda _: time.sleep(amount)


def grab_identifier(m):
    pass


# endregion


def get_rest_api_settings():
    vs_code_settings = None
    with open(
        os.path.expanduser("~/Library/Application Support/Code/User/settings.json")
    ) as fh:
        contents = fh.read()
        vs_code_settings = json.loads(contents)
    if vs_code_settings is None:
        print("Could not load VS Code Settings")
        return None, None, None
    if "rest.api" not in vs_code_settings:
        print("Rest API not configured.")
        return None, None, None
    rest_api_settings = vs_code_settings["rest.api"]
    port = rest_api_settings.get("port", None)
    talon_users = [
        u for u in rest_api_settings.get("users", {}) if u["name"] == "talon"
    ]
    if len(talon_users) != 1:
        print(
            "Rest API needs a single user named 'talon' with write access.  See docs."
        )
        return None, None, None
    username = talon_users[0]["name"]
    password = talon_users[0]["password"]
    return port, username, password


def send_api_command(*commands):
    def _send():
        port, username, password = get_rest_api_settings()
        if port:
            for cmds in commands:
                for cmd in cmds:
                    print("Sending {}".format(cmd))
                    response = requests.post(
                        "http://localhost:{}/api/commands/{}".format(port, cmd),
                        timeout=(0.05, 3.05),
                        auth=(username, password),
                    )
                    response.raise_for_status()
        else:
            print("Rest API does not have 'port' setting.")

    threading.Thread(target=_send).start()


def go_to_line(drop=1):
    def handler(m):
        line = text_to_number(m._words[drop:])
        if int(line) == 0:
            print("Not sending, arg was 0")
            return
        port, username, password = get_rest_api_settings()
        if port:
            pos = {"line": line - 1, "character": 0}
            selection = {"start": pos, "end": pos}
            response = requests.post(
                "http://localhost:{}/api/talonLine".format(port),
                timeout=(0.05, 3.05),
                auth=(username, password),
                json=selection,
            )
            response.raise_for_status()
            return response.text
        else:
            print("Rest API does not have 'port' setting.")

    return handler


def select_lines(drop=1):
    def handler(m):
        start, end = text_to_range(m._words[drop:])
        port, username, password = get_rest_api_settings()
        if port:
            startPos = {"line": start - 1, "character": 0}
            endPos = {"line": end - 1, "character": 9999}
            selection = {"start": startPos, "end": endPos}
            response = requests.post(
                "http://localhost:{}/api/talonLine".format(port),
                timeout=(0.05, 3.05),
                auth=(username, password),
                json=selection,
            )
            response.raise_for_status()
            return response.text
        else:
            print("Rest API does not have 'port' setting.")

    return handler


def vscode_command(*cmds):
    return lambda _: send_api_command(cmds)


def vscode_search(direction, drop=2):
    def handler(m):
        pattern = " ".join([str(w) for w in m.dgndictation[0]._words])
        port, username, password = get_rest_api_settings()
        if port:
            response = requests.post(
                "http://localhost:{}/api/talonSearch".format(port),
                timeout=(0.05, 3.05),
                auth=(username, password),
                json={"direction": direction, "string": pattern},
            )
            response.raise_for_status()
            return response.text
        else:
            print("Rest API does not have 'port' setting.")

    return handler


# group = ContextGroup("vscode")
ctx = Context("vscode", bundle="com.microsoft.VSCode")  # , group=group)
ctx.keymap(
    {
        "complete": vscode_command("editor.action.triggerSuggest"),
        # "smarter": vscode_command("action"),
        # "finish": vscode_command("action"),
        "zoom": vscode_command("workbench.action.maximizeEditor"),
        "find (usage | usages)": vscode_command(
            "editor.action.referenceSearch.trigger"
        ),
        "(refactor | reflector) [<dgndictation>]": [
            vscode_command("editor.action.refactor"),
            text,
        ],
        "fix [this]": vscode_command("editor.action.quickFix"),
        "visit declaration": vscode_command("editor.action.goToDeclaration"),
        "visit (implementers | implementations)": vscode_command(
            "editor.action.goToImplementation"
        ),
        "visit type": vscode_command("editor.action.goToTypeDefinition"),
        "(select previous | trail) [<dgndictation>]": vscode_search("backwards"),
        "(select next | crew) [<dgndictation>]": vscode_search("forwards"),
        # "search everywhere [for] [<dgndictation>]": [
        #     vscode_command("action"),
        #     text,
        # ],
        "find [<dgndictation>]": [vscode_command("actions.find"), delay(), text],
        "find this": vscode_command("actions.findWithSelection"),
        "(template | snippet) [<dgndictation>]": [
            vscode_command("editor.action.insertSnippet"),
            delay(),
            text,
        ],
        "select less": vscode_command("editor.action.smartSelect.shrink"),
        "select more": vscode_command("editor.action.smartSelect.grow"),
        f"select line {_optional_numerals}": [
            go_to_line(drop=2),
            vscode_command("cursorHome", "cursorEndSelect"),
        ],
        "select this line": [vscode_command("cursorHome", "cursorEndSelect")],
        f"select (lines | line) {_optional_numerals} until {_optional_numerals}": select_lines(
            drop=2
        ),
        "(clean | clear) line": [vscode_command("cursorLineStart", "deleteAllRight")],
        "(delete | remove) line": vscode_command("editor.action.deleteLines"),
        "(delete | clear) to end": vscode_command("deleteAllRight"),
        "(delete | clear) to start": vscode_command("deleteAllLeft"),
        "drag up": vscode_command("editor.action.moveLinesUpAction"),
        "drag down": vscode_command("editor.action.moveLinesDownAction"),
        "duplicate": vscode_command("editor.action.copyLinesDownAction"),
        "(go | jump) back": vscode_command("workbench.action.navigateBack"),
        "(go | jump) forward": vscode_command("workbench.action.navigateForward"),
        "comment": vscode_command("editor.action.commentLine"),
        "(action | please) [<dgndictation>]": [
            vscode_command("workbench.action.showCommands"),
            delay(),
            text,
        ],
        f"(go to | jump to) {_optional_numerals}": [
            go_to_line(drop=2),
            vscode_command("cursorHome"),
        ],
        f"(go | jump) to end of {_optional_numerals}": [
            go_to_line(drop=4),
            vscode_command("cursorHome"),
        ],
    }
)
# group.load()
