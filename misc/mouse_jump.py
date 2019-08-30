import json
import os
from collections import defaultdict

from talon.voice import Context

from talon import app, ctrl, ui, resource
from .. import utils

warps_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "warps.json")
loaded_warps = defaultdict(dict)
try:
    with resource.open(warps_file) as fh:
        loaded_warps.update(json.load(fh))
except FileNotFoundError:
    pass


class MouseWarp:
    def __init__(self):
        self.data = loaded_warps

    def mark(self, name):
        window = ui.active_window()
        bundle = window.app.bundle
        x, y = ctrl.mouse_pos()
        rect = window.rect
        center_x, center_y = rect.center
        x_offset = x - (rect.left if x < center_x else rect.right)
        y_offset = y - (rect.top if y < center_y else rect.bot)
        app.notify(f"Marked: {name}")
        self.data[bundle][name] = [int(x_offset), int(y_offset)]
        self.dump()

    def warp(self, name):
        window = ui.active_window()
        bundle = window.app.bundle
        try:
            x_offset, y_offset = self.data[bundle][name]
        except KeyError:
            return
        rect = window.rect
        x = rect.left + (x_offset % rect.width)
        y = rect.top + (y_offset % rect.height)
        ctrl.mouse(x, y)

    def warps(self):
        try:
            window = ui.active_window()
            bundle = window.app.bundle
            return self.data[bundle].keys()
        except Exception as e:
            print(e)
            return []

    def dump(self):
        with open(warps_file, "w") as f:
            json.dump(self.data, f, indent=2)


mj = MouseWarp()
ctx = Context("warp")
ctx.keymap(
    {
        "mark <dgndictation> [over]": [
            lambda m: mj.mark(utils.join_words(utils.parse_words(m))),
            lambda _: ctx.set_list("warps", mj.warps()),
        ],
        "warp {warp.warps}": [lambda m: mj.warp(m["warp.warps"][0])],
        "list warps": [lambda _: app.notify("Warps:\n" + "\n".join(mj.warps()))],
        "click {warp.warps}": [
            lambda m: mj.warp(m["warp.warps"][0]),
            lambda _: ctrl.mouse_click(button=0),
        ],
    }
)
ctx.set_list("warps", mj.warps())
