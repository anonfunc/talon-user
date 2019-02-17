import time

from talon import cron, ctrl, tap
from talon.voice import Context
from talon_plugins import eye_mouse, eye_zoom_mouse

ctx = Context("mouse")

x, y = ctrl.mouse_pos()
mouse_history = [(x, y, time.time())]
force_move = None


def on_move(_, e):
    time_ = (e.x, e.y, time.time())
    # print(time_)
    mouse_history.append(time_)
    if force_move:
        e.x, e.y = force_move
        return True
    return False


tap.register(tap.MMOVE, on_move)


# noinspection PyProtectedMember
def click_pos(m, from_end=False):
    word = m._words[0]
    if from_end:
        word = m._words[-1]
    # print(f"word is {word} {word.start} {word.end}")
    # start = (word.start + min((word.end - word.start) / 2, 0.100)) / 1000.0
    word_time = word.end / 1000.0
    # if from_end:
    #     word_time = word.end / 1000.0
    # print(f"word start is {word_time}, now is {time.time()}")
    for pos in reversed(mouse_history):
        if pos[2] < word_time:
            # print(f"pos is {pos}")
            return pos[:2]
    return mouse_history[-1][:2]


def delayed_click(m, button=0, times=1, from_end=False, mods=None):
    if mods is None:
        mods = []
    old = eye_mouse.config.control_mouse
    eye_mouse.config.control_mouse = False
    x, y = click_pos(m, from_end=from_end)
    ctrl.mouse(x, y)
    for key in mods:
        ctrl.key_press(key, down=True)
    ctrl.mouse_click(x, y, button=button, times=times, wait=16000)
    for key in mods[::-1]:
        ctrl.key_press(key, up=True)
    time.sleep(0.032)
    eye_mouse.config.control_mouse = old


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
        global scrollAmount
        # print("amount is", amount)
        if (scrollAmount >= 0) == (amount >= 0):
            scrollAmount += amount
        else:
            scrollAmount = amount
        ctrl.mouse_scroll(y=amount)

    return scroll


def adv_click(button, *mods, **kwargs):
    def click(e):
        for key in mods:
            ctrl.key_press(key, down=True)
        delayed_click(e)
        for key in mods[::-1]:
            ctrl.key_press(key, up=True)

    return click


def control_mouse(m):
    ctrl.mouse(0, 0)
    eye_mouse.control_mouse.toggle()
    if eye_zoom_mouse.zoom_mouse.enabled:
        eye_zoom_mouse.zoom_mouse.enable()


def control_zoom_mouse(m):
    ctrl.mouse(0, 0)
    if eye_zoom_mouse.zoom_mouse.enabled:
        eye_zoom_mouse.zoom_mouse.disable()
    else:
        eye_zoom_mouse.zoom_mouse.enable()

    eye_zoom_mouse.zoom_mouse.toggle()
    if eye_mouse.control_mouse.enabled:
        eye_mouse.control_mouse.toggle()


def scrollMe():
    global scrollAmount
    if scrollAmount:
        ctrl.mouse_scroll(by_lines=False, y=scrollAmount / 10)


def startScrolling(m):
    global scrollJob
    scrollJob = cron.interval("60ms", scrollMe)


def stopScrolling(m):
    global scrollAmount, scrollJob
    scrollAmount = 0
    cron.cancel(scrollJob)


scrollAmount = 0
scrollJob = None

hideJob = None


def toggle_cursor(show):
    def _toggle(_):
        global hideJob
        ctrl.cursor_visible(show)
        if show:
            cron.cancel(hideJob)
        else:
            hideJob = cron.interval("500ms", lambda: ctrl.cursor_visible(show))

    return _toggle


keymap = {
    "hide cursor": toggle_cursor(False),
    "show cursor": toggle_cursor(True),
    # "debug overlay": lambda m: eye.on_menu("Eye Tracking >> Show Debug Overlay"),
    "(gaze | control mouse)": control_mouse,
    "zoom mouse": control_zoom_mouse,
    # "camera overlay": lambda m: eye.on_menu("Eye Tracking >> Show Camera Overlay"),
}

click_keymap = {
    "click": delayed_click,
    "click right": delayed_right_click,
    "click double": delayed_dubclick,
    "click triple": delayed_tripclick,
    "click drag": mouse_drag,
    "click release": mouse_release,
    "wheel down": mouse_scroll(30),
    "wheel down continuous": [mouse_scroll(30), startScrolling],
    "wheel up": mouse_scroll(-30),
    "wheel up continuous": [mouse_scroll(-30), startScrolling],
    "wheel stop": stopScrolling,
    "click command": adv_click(0, "cmd"),
    "click control": adv_click(0, "ctrl"),
    "click (option | opt)": adv_click(0, "alt"),
    "click shift": adv_click(0, "shift"),
    "click (shift alt | alt shift)": adv_click(0, "alt", "shift"),
    "click (shift double | double shift)": adv_click(0, "shift", times=2),
}
keymap.update(click_keymap)

ctx.keymap(keymap)

ctrl.cursor_visible(True)
