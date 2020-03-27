from talon import app, tap, ui
from talon.engine import engine
from talon.voice import Context, ContextGroup, talon
from talon_plugins import speech, microphone

from .. import utils
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
            lambda m: _mimic("wake up".split()),
        ],
        "dictation mode": [
            # lambda m: speech.set_enabled(False),
            lambda _: app.notify("Dictation mode"),
            lambda m: _mimic("go to sleep".split()),
            lambda m: dictation_group.enable(),
        ],
        "talon mode": [
            lambda m: speech.set_enabled(True),
            lambda _: app.notify("Talon mode"),
            lambda m: dictation_group.disable(),
            lambda m: _mimic("go to sleep".split()),
        ],
        "full sleep mode": [
            lambda m: speech.set_enabled(False),
            lambda m: dictation_group.disable(),
            lambda m: _mimic("go to sleep".split()),
        ],
    }
)
sleep_group.load()


def _mimic(words):
    if engine.endpoint:
        engine.mimic(words)


def sleep_hotkey(typ, e):
    # print(e)
    if e == 'cmd-alt-ctrl-shift-tab' and e.down:
        speech.set_enabled(not speech.talon.enabled)
        if speech.talon.enabled:
            if microphone.manager.active_mic() is None:
                utils.use_mic("krisp microphone")
            utils.mic_uses_volume({
                "Plantronics Blackwire 435": 100,
                "ATR2USB": 80,
                "AndreaMA": 35,
            })
            if not engine.endpoint:
                ui.launch(bundle="com.dragon.dictate")
        else:
            utils.set_input_volume(0)  # Fallback, only override with present mic.
        e.block()
    return True


tap.register(tap.HOOK | tap.KEY, sleep_hotkey)

speech.set_enabled(False)


# Default to krisp on startup, if present.
def _use_krisp():
    utils.use_mic("krisp microphone")


# _use_krisp()
# Start at login, but off.
utils.use_mic("None")
