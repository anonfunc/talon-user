from talon import ui
from talon.voice import Context, Key, Rep, Str, Word, press

from ..utils import parse_word

apps = {}


def switch_app(m):
    # noinspection PyProtectedMember
    name = parse_word(m._words[1])
    full = apps.get(name)
    if not full:
        return
    for app in ui.apps():
        if app.name == full:
            app.focus()
            break


ctx = Context("switcher")
ctx.keymap({"focus {switcher.apps}": switch_app})


def update_lists():
    global apps
    new = {}
    for app in ui.apps():
        if not app.windows():
            continue
        words = app.name.split(" ")
        for word in words:
            if word and word not in new and len(word) > 1:
                new[word] = app.name
        new[app.name] = app.name
    if set(new.keys()) == set(apps.keys()):
        return
    # print(new)
    ctx.set_list("apps", new.keys())
    apps = new


def ui_event(event, arg):
    if event in ('win_open', 'win_closed') and arg.app.name == 'Amethyst':
        return
    if event in ("app_activate", "app_launch", "app_close", "win_open", "win_close"):
        update_lists()


ui.register("", ui_event)
update_lists()
