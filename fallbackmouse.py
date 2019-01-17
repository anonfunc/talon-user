import time

from talon import ctrl, tap
from talon.audio import noise
from talon.track.geom import Point2d
from talon.voice import Context, Key

ctx = Context("mouse")

x, y = ctrl.mouse_pos()
mouse_history = [(x, y, time.time())]
force_move = None


def on_move(typ, e):
    x0, y0 = mouse_history[-1][0:2]
    # noinspection PyShadowingNames
    x, y = e.x, e.y
    if abs(x - x0) < 5 and abs(y - y0) < 5:
        return

    mouse_history.append((x, y, time.time()))


# if force_move:
#     e.x, e.y = force_move
#     return True


tap.unregister(tap.MMOVE, on_move)
tap.register(tap.MMOVE, on_move)


def click_pos(m):
    # noinspection PyProtectedMember
    word = m._words[0]
    start = (word.start + min((word.end - word.start) / 2, 0.100)) / 1000.0
    diff, pos = min([(abs(start - pos[2]), pos) for pos in mouse_history])
    return pos[:2]


def delayed_click(m, button=0, times=1):
    # noinspection PyShadowingNames
    x, y = click_pos(m)
    ctrl.mouse(x, y)
    ctrl.mouse_click(x, y, button=button, times=times, wait=16000)
    time.sleep(0.032)


def delayed_right_click(m):
    delayed_click(m, button=1)


def delayed_dubclick(m):
    delayed_click(m, button=0, times=2)


def delayed_tripclick(m):
    delayed_click(m, button=0, times=3)


def mouse_drag(m):
    x, y = click_pos(m)
    ctrl.mouse_click(x, y, down=True)


def mouse_release(m):
    x, y = click_pos(m)
    ctrl.mouse_click(x, y, up=True)


def mouse_scroll(amount):
    def scroll(m):
        # print("amount is", amount)
        ctrl.mouse_scroll(x=amount)

    return scroll


def adv_click(button, *mods, **kwargs):
    def click(e):
        for key in mods:
            ctrl.key_press(key, down=True)
        delayed_click(e)
        for key in mods[::-1]:
            ctrl.key_press(key, up=True)

    return click
