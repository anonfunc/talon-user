import json
import os
import threading
import time

import requests
from talon import ctrl
from talon.voice import Context

from ...utils import optional_numerals, text, text_to_number, text_to_range

try:
    from ...misc.mouse import delayed_click
except ImportError:
    print("Fallback mouse click logic")

    def delayed_click():
        ctrl.mouse_click(button=0)


def delay(amount=0.1):
    return lambda _: time.sleep(amount)


def get_rest_api_settings():
    vs_code_settings = None
    with open(
        os.path.expanduser("~/Library/Application Support/Code/User/settings.json")
    ) as fh:
        contents = fh.read()
        try:
            vs_code_settings = json.loads(contents)
        except json.JSONDecodeError:
            pass
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
        # noinspection PyProtectedMember
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
        # noinspection PyProtectedMember
        start, end = text_to_range(m._words[drop:])
        port, username, password = get_rest_api_settings()
        if port:
            start_pos = {"line": start - 1, "character": 0}
            end_pos = {"line": end - 1, "character": 9999}
            selection = {"start": start_pos, "end": end_pos}
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


def vscode_search(direction):
    def handler(m):
        # noinspection PyProtectedMember
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
        "(select previous | trail) <dgndictation>": vscode_search("backwards"),
        "(select next | crew) <dgndictation>": vscode_search("forwards"),
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
        f"select line {optional_numerals}": [
            go_to_line(drop=2),
            vscode_command("cursorHome", "cursorEndSelect"),
        ],
        "select this line": [vscode_command("cursorHome", "cursorEndSelect")],
        f"select (lines | line) {optional_numerals} until {optional_numerals}": select_lines(
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
        f"(go to | jump to) {optional_numerals}": [
            go_to_line(drop=2),
            vscode_command("cursorHome"),
        ],
        f"(go | jump) to end of {optional_numerals}": [
            go_to_line(drop=4),
            vscode_command("cursorHome"),
        ],
    }
)
# group.load()
