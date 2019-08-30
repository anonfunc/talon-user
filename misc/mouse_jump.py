from collections import defaultdict
import json
import os

from talon import canvas, ctrl, ui, resource
from talon.voice import Context, ContextGroup, Key
from talon.voice import talon as talon_cg
from talon_plugins import speech

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
        corner = None
        x_offset, y_offset = 0, 0
        window_x_midpoint = window.rect.x + window.rect.width // 2
        window_y_midpoint = window.rect.y + window.rect.height // 2
        if x < window_x_midpoint:
            x_offset = x - window.rect.x
        else:
            x_offset = -(window.rect.x + window.rect.width - x)
        if y <= window_y_midpoint:
            y_offset = y - window.rect.y
        else:
            y_offset = -(window.rect.y + window.rect.height - y)

        self.data[bundle][name] = [int(x_offset), int(y_offset)]
        # print(f"Marked self.data[{bundle}][{name}] = {[x_offset, y_offset]}")
        self.dump()

    def warp(self, name):
        window = ui.active_window()
        bundle = window.app.bundle
        x, y = 0, 0
        try:
            x_offset, y_offset = self.data[bundle][name]
        except KeyError:
            return
        if x_offset > 0:
            x = window.rect.x + x_offset
        else:
            x = window.rect.x + window.rect.width + x_offset

        if y_offset > 0:
            y = window.rect.y + y_offset
        else:
            y = window.rect.y + window.rect.height + y_offset
        # print(f"Warp to self.data[{bundle}][{name}] = {[x_offset, y_offset]} ({[x, y]})")
        ctrl.mouse(x, y)

    def warps(self):
        window = ui.active_window()
        bundle = window.app.bundle
        return self.data[bundle].keys()

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
        "warp {warp.warps}": [
            lambda m: mj.warp(m["warp.warps"][0]),
        ],
         "click {warp.warps}": [
            lambda m: mj.warp(m["warp.warps"][0]),
            lambda _: ctrl.mouse_click(button=0),
        ],
    }
)
ctx.set_list("warps", mj.warps())
