from talon.voice import Context, Key

from .. import utils

globalctx = Context("ticktickGlobal")
globalctx.keymap(
    {
        # Rebound, conflicted with Jetbrains action search
        "quick task [<dgndictation>] [over]": [
            Key("shift-alt-cmd-a"),
            utils.delay(0.2),
            utils.text,
        ],
        # Rebound, didn't trust it
        "toggle tick mini": [Key("shift-alt-cmd-o")],
        # Rebound, didn't trust it
        "toggle tick main": [Key("shift-alt-cmd-e")],
        # Rebound, didn't trust it
        "toggle tick pomo": [Key("shift-alt-cmd-p")],
    }
)

ctx = Context("ticktick", bundle="com.TickTick.task.mac")
ctx.keymap(
    {
        "sync task": Key("cmd-s"),
        "search task": Key("cmd-f"),
        "search task [<dgndictation>] [over]": [Key("cmd-f"), utils.delay(0.3), utils.text],
        "add task": Key("cmd-n"),
        "add task [<dgndictation>] [over]": [Key("cmd-n"), utils.delay(0.3), utils.text],
        "complete task": Key("shift-cmd-m"),
        "clear date": Key("cmd-0"),
        "set today": Key("cmd-1"),
        "set tomorrow": Key("cmd-2"),
        "set next week": Key("cmd-3"),

        # Rebound, existing was ctrl only, conflict with spaces
        "set no priority": Key("cmd-ctrl-0"),
        "set low priority": Key("cmd-ctrl-1"),
        "set medium priority": Key("cmd-ctrl-2"),
        "set high priority": Key("cmd-ctrl-3"),

        # Back to defaults
        "go today": Key("ctrl-cmd-t"),
        "go tomorrow": Key("ctrl-cmd-t"),
        "go next seven days": Key("alt-cmd-n"),
        "go all": Key("alt-cmd-a"),
        "go calendar": Key("ctrl-cmd-c"),
        "go assigned": Key("ctrl-cmd-a"),
        "go complete": Key("alt-cmd-c"),
    }
)
