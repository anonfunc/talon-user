from talon.voice import Context, ContextGroup, Key, press
from talon import ctrl
from user.std import text
import time


def delay(amount):
    return lambda _: time.sleep(amount)

# I don't want to interleave jira navigation with other commands, like dictation.
group = ContextGroup("jira")
ctx = Context('jira', func=lambda app, win: win.title.endswith(' JIRA2'), group=group)
ctx.vocab = [
    'sub-task',
    'Dwight',
]
ctx.keymap({
    'dashboard': Key('g d'),
    'boards': Key('g b'),
    'issues': Key('g i'),
    'find': Key('/'),
    'create': Key("c"),
    'assign [to] <dgndictation> [over]': [Key("a"), delay(0.6), text],
    'assign to me': Key("i"),
    'comment': Key("m"),
    'edit': Key("e"),
    'action <dgndictation> [over]': [Key("."), delay(0.6), text],
    'submit': Key("ctrl+return"),
    'copy link': Key("cmd+l cmd+c"),
    'copy id': Key("cmd+l right alt+shift+left alt+shift+left cmd+c"),
})
group.load()