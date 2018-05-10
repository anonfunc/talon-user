import time
from talon.voice import Context, Key, ctrl

ctx = Context("mouse")


def adv_click(button, *mods, **kwargs):

    def click(e):
        for key in mods:
            ctrl.key_press(key, down=True)
        ctrl.mouse_click(button=button, **kwargs)
        for key in reversed(mods):
            ctrl.key_press(key, up=True)

    return click


def mouse_drag(m):
    ctrl.mouse_click(0, down=True)


def mouse_release(m):
    ctrl.mouse_click(0, up=True)


def mouse_scroll(amount):

    def scroll(m):
        print("amount is", amount)
        ctrl.mouse_scroll(x=amount)

    return scroll


keymap = {
    "click drag": mouse_drag,
    "click release": mouse_release,
    "click": adv_click(0),
    "click right": adv_click(1),
    "scrodge": mouse_scroll(10),
    "scroop": mouse_scroll(-10),
    "click control": adv_click(0, "ctrl"),
    "chipper": adv_click(0, "ctrl"),
    "click command": adv_click(0, "cmd"),
    "click option": adv_click(0, "alt"),
    "click shift": adv_click(0, "shift"),
    "click shift alt": adv_click(0, "alt", "shift"),
    "click double": adv_click(0, times=2),
    "click triple": adv_click(0, times=3),
    "click shift double": adv_click(0, "shift", times=2),
}

ctx.keymap(keymap)
