from talon import app, tap
from talon.engine import engine
from talon.voice import Context, ContextGroup, talon
from talon_plugins import speech

from ..misc.dictation import dictation_group

sleep_group = ContextGroup("sleepy")
sleepy = Context("sleepy", group=sleep_group)
sleepy.keymap(
    {
        "talon sleep": lambda m: speech.set_enabled(False),
        "talon wake": lambda m: speech.set_enabled(True),
        "dragon mode": [
            lambda m: speech.set_enabled(False),
            lambda _: app.notify("Dragon mode"),
            lambda m: dictation_group.disable(),
            lambda m: engine.mimic("wake up".split()),
        ],
        "dictation mode": [
            # lambda m: speech.set_enabled(False),
            lambda _: app.notify("Dictation mode"),
            lambda m: engine.mimic("go to sleep".split()),
            lambda m: dictation_group.enable(),
        ],
        "talon mode": [
            lambda m: speech.set_enabled(True),
            lambda _: app.notify("Talon mode"),
            lambda m: dictation_group.disable(),
            lambda m: engine.mimic("go to sleep".split()),
        ],
        "full sleep mode": [
            lambda m: speech.set_enabled(False),
            lambda m: dictation_group.disable(),
            lambda m: engine.mimic("go to sleep".split()),
        ],
    }
)
sleep_group.load()


def sleep_hotkey(typ, e):
    # print(e)
    if e == 'cmd-alt-ctrl-shift-tab' and e.down:
        speech.set_enabled(not speech.talon.enabled)
        e.block()
    return True


tap.register(tap.HOOK | tap.KEY, sleep_hotkey)
