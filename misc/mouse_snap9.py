import math
import time

from talon import canvas, ctrl, ui
from talon.voice import Context, ContextGroup
from talon_plugins import speech, eye_mouse, eye_zoom_mouse

from .mouse import click_keymap


class MouseSnapNine:
    def __init__(self):
        self.states = []
        # self.screen_index = 0
        self.screen = ui.screens()[0]
        self.offset_x = self.screen.x
        self.offset_y = self.screen.y
        self.width = self.screen.width
        self.height = self.screen.height
        self.states.append((self.offset_x, self.offset_y, self.width, self.height))
        self.mcanvas = canvas.Canvas.from_screen(self.screen)
        self.active = False
        self.moving = False
        self.count = 0
        self.was_eye_tracking = False

    #     tap.register(tap.MMOVE, self.on_move)
    #
    # def on_move(self, typ, e):
    #     if typ != tap.MMOVE or not self.active:
    #         return
    #     x, y = self.pos()
    #     last_pos = self.states[-1]
    #     x2, y2 = last_pos[0] + last_pos[2]//2, last_pos[1] + last_pos[3]//2
    #     # print("moved ", e, x, y)
    #     if (e.x, e.y) != (x, y) and (e.x, e.y) != (x2, y2):
    #         self.stop(None)

    def start(self, *_):
        if self.active:
            return
        # noinspection PyUnresolvedReferences
        if eye_zoom_mouse.zoom_mouse.enabled:
            return
        if eye_mouse.control_mouse.enabled:
            self.was_eye_tracking = True
            eye_mouse.control_mouse.toggle()
        if self.mcanvas is not None:
            self.mcanvas.unregister("draw", self.draw)
        self.mcanvas.register("draw", self.draw)
        self.active = True

    def stop(self, *_):
        self.mcanvas.unregister("draw", self.draw)
        self.active = False
        if self.was_eye_tracking and not eye_mouse.control_mouse.enabled:
            eye_mouse.control_mouse.toggle()
        self.was_eye_tracking = False

    def draw(self, canvas):
        paint = canvas.paint
        paint.color = "ff0000"
        canvas.draw_line(
            self.offset_x + self.width // 3,
            self.offset_y,
            self.offset_x + self.width // 3,
            self.offset_y + self.height,
        )
        canvas.draw_line(
            self.offset_x + 2 * self.width // 3,
            self.offset_y,
            self.offset_x + 2 * self.width // 3,
            self.offset_y + self.height,
        )

        canvas.draw_line(
            self.offset_x,
            self.offset_y + self.height // 3,
            self.offset_x + self.width,
            self.offset_y + self.height // 3,
        )
        canvas.draw_line(
            self.offset_x,
            self.offset_y + 2 * self.height // 3,
            self.offset_x + self.width,
            self.offset_y + 2 * self.height // 3,
        )

        for row in range(3):
            for col in range(3):
                canvas.draw_text(
                    f"{row*3+col+1}",
                    self.offset_x + self.width / 6 + col * self.width / 3,
                    self.offset_y + self.height / 6 + row * self.height / 3,
                )

    def narrow(self, which, move=True):
        self.save_state()
        row = int(which - 1) // 3
        col = int(which - 1) % 3
        self.offset_x += int(col * self.width // 3)
        self.offset_y += int(row * self.height // 3)
        self.width //= 3
        self.height //= 3
        if move:
            ctrl.mouse_move(*self.pos())
        self.count += 1
        if self.count >= 4:
            self.reset(None)

    def pos(self):
        return self.offset_x + self.width // 2, self.offset_y + self.height // 2

    def reset(self, pos=-1):
        def _reset(m):
            self.save_state()
            self.count = 0
            x, y = ctrl.mouse_pos()

            if pos >= 0:
                self.screen = ui.screens()[pos]
            else:
                self.screen = ui.screen_containing(x, y)

            # print(screens)
            # self.screen = screens[self.screen_index]
            self.offset_x = self.screen.x
            self.offset_y = self.screen.y
            self.width = self.screen.width
            self.height = self.screen.height
            if self.mcanvas is not None:
                self.mcanvas.unregister("draw", self.draw)
            self.mcanvas = canvas.Canvas.from_screen(self.screen)
            self.mcanvas.register("draw", self.draw)
            if eye_mouse.control_mouse.enabled:
                self.was_eye_tracking = True
                eye_mouse.control_mouse.toggle()
            if self.was_eye_tracking and self.screen == ui.screens()[0]:
                # if self.screen == ui.screens()[0]:
                self.narrow_to_pos(x, y)
                self.narrow_to_pos(x, y)
                # self.narrow_to_pos(x, y)
            # print(self.offset_x, self.offset_y, self.width, self.height)
            # print(*self.pos())

        return _reset

    def narrow_to_pos(self, x, y):
        col_size = int(self.width // 3)
        row_size = int(self.height // 3)
        col = math.floor((x - self.offset_x) / col_size)
        row = math.floor((y - self.offset_y) / row_size)
        # print(f"Narrow to {row} {col} {1 + col + 3 * row}")
        self.narrow(1 + col + 3 * row, move=False)

    def save_state(self):
        self.states.append((self.offset_x, self.offset_y, self.width, self.height))

    def go_back(self, _):
        last_state = self.states.pop()
        self.offset_x, self.offset_y, self.width, self.height = last_state
        self.count -= 1


def narrow(m):
    for d in m["mouseSnapNine.digits"]:
        mg.narrow(int(digits[d]))
        time.sleep(0.1)


digits = dict((str(n), n) for n in range(1, 10))
digits.update(
    {  # Needed with built in engine?
        "for": 4,
        r"one\\number": 1,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
    }
)

mg = MouseSnapNine()
group = ContextGroup("snapNine")
ctx = Context("mouseSnapNine", group=group)
keymap = {
    "{mouseSnapNine.digits}+": narrow,
    "(oops | back)": mg.go_back,
    "(reset | clear | escape)": mg.reset(),
    "left": mg.reset(1),
    "middle": mg.reset(0),
    "right": mg.reset(2),
    "(done | grid | mouse grid | mousegrid)": [
        mg.stop,
        lambda _: ctx.unload(),
        lambda _: speech.set_enabled(True),
    ],
}
keymap.update(
    {
        k: [v, mg.stop, lambda _: ctx.unload(), lambda _: speech.set_enabled(True)]
        for k, v in click_keymap.items()
    }
)
ctx.keymap(keymap)
ctx.set_list("digits", digits.keys())
group.load()
ctx.unload()


def do_start_digits(m):
    try:
        for d in m["mouseSnapNineStarter.digits"]:
            mg.narrow(int(digits[d]))
        ctrl.mouse_move(*mg.pos())
    except KeyError:
        pass


startCtx = Context("mouseSnapNineStarter")
startKeymap = {
    "(grid | mouse grid | mousegrid) [{mouseSnapNineStarter.digits}+]": [
        mg.reset(),
        mg.start,
        lambda _: ctx.load(),
        lambda _: speech.set_enabled(False),
        do_start_digits,
    ],
    # "snap done": [mg.stop, lambda _: ctx.unload()],
}
startKeymap.update(
    {
        "(grid | mouse grid | mousegrid) [{mouseSnapNineStarter.digits}+] click": [
            mg.reset(),
            mg.start,
            do_start_digits,
            lambda _: ctrl.mouse_click(button=0),
            mg.stop,
        ],
        "(grid | mouse grid | mousegrid) [{mouseSnapNineStarter.digits}+] right click": [
            mg.reset(),
            mg.start,
            do_start_digits,
            lambda _: ctrl.mouse_click(button=1),
            mg.stop,
        ],
    }
)

startCtx.keymap(startKeymap)
startCtx.set_list("digits", digits.keys())
# mg.start()
# Hot reload while grid is active is very confusing without this.
speech.set_enabled(True)
