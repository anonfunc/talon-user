import json
import subprocess
import time

import requests
from talon import cron
from talon.voice import Context, ContextGroup, Key, Str, talon
from talon.ui import active_app

from .vscode import get_rest_api_settings

terminals = ("com.apple.Terminal", "com.googlecode.iterm2")

def TerminalContext(app, win):
    global _terminalContextJob
    global _lastEditorSelection
    if app.bundle in terminals:
        _lastEditorSelection = ""
        return True
    elif app.bundle == "com.microsoft.VSCode":
        return is_vscode_terminal()
    return False

_lastEditorSelection = ""
_lastTerminalLsof = None
_inTerminal = False

def is_vscode_terminal():
    global _lastEditorSelection
    global _lastTerminalLsof
    global _inTerminal
    port, username, password = get_rest_api_settings()
    if port:
        response = requests.get(
            "http://localhost:{}/api/talonTerminal".format(port),
            timeout=(0.05, 3.05),
            auth=(username, password),
        )
        response.raise_for_status()
        data = response.json()
        # print(data)
        editorSelection = json.dumps(data["data"].get("activeEditorSelection", None), sort_keys=True)
        terminal = json.dumps(data["data"].get("activeTerminal", None), sort_keys=True)

        if _lastEditorSelection == editorSelection:
            if "activeTerminal" in data["data"]:
                if not _inTerminal:
                    # If we think we might be in a terminal, we know activity happened there if our tty's offsets have changed.
                    # lsof is an easy way to check that.
                    if data["data"].get("activeTerminalPid", 0):
                        lsof = subprocess.check_output(["lsof", "-p", str(data["data"]["activeTerminalPid"])])
                    if _lastTerminalLsof and lsof != _lastTerminalLsof:
                        _inTerminal = True
                    _lastTerminalLsof = lsof
        else:
            _inTerminal = False
        
        _lastEditorSelection = editorSelection
        # if _inTerminal:
        #     print("TERMINAL: {}".format(editorSelection))
        return _inTerminal
    else:
        print("Rest API does not have 'port' setting.")
    return False

ctx = Context("vscodeterminal", func=TerminalContext)
ctx.keymap({
    "testing": "vscode testing"
})

 
def _updateScope():
    global _terminalContextJob
    if active_app().bundle == "com.microsoft.VSCode":
        print("In vscode, updating scope...")
        talon.update_scope()
    else:
        cron.cancel(_terminalContextJob)
        _terminalContextJob = None

_terminalContextJob = cron.interval('2s', _updateScope)