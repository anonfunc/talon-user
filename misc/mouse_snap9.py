from talon import canvas, ctrl, ui
from talon.voice import Context, ContextGroup, Key
from talon_plugins import speech

from .mouse import click_keymap


class MouseSnapNine:
    def __init__(self):
        self.states = []
        self.main_screen = ui.main_screen()
        self.offset_x = 0
        self.offset_y = 0
        self.width = self.main_screen.width
        self.height = self.main_screen.height
        self.states.append((self.offset_x, self.offset_y, self.width, self.height))
        self.mcanvas = canvas.Canvas.from_screen(self.main_screen)
        self.active = False
        self.count = 0

    def start(self, *_):
        if self.active:
            return
        self.mcanvas.register('draw', self.draw)
        self.active = True

    def stop(self, *_):
        self.mcanvas.unregister('draw', self.draw)
        self.active = False

    def draw(self, canvas):
        paint = canvas.paint
        paint.color = "ff0000"
        canvas.draw_line(self.offset_x + self.width // 3, self.offset_y, self.offset_x + self.width // 3,
                         self.offset_y + self.height)
        canvas.draw_line(self.offset_x + 2 * self.width // 3, self.offset_y, self.offset_x + 2 * self.width // 3,
                         self.offset_y + self.height)

        canvas.draw_line(self.offset_x, self.offset_y + self.height // 3, self.offset_x + self.width,
                         self.offset_y + self.height // 3)
        canvas.draw_line(self.offset_x, self.offset_y + 2 * self.height // 3, self.offset_x + self.width,
                         self.offset_y + 2 * self.height // 3)

        for row in range(3):
            for col in range(3):
                canvas.draw_text(f"{row*3+col+1}", self.offset_x + self.width/6 + col * self.width/3,
                                 self.offset_y + self.height / 6 + row * self.height/3)

    def narrow(self, which):
        self.save_state()
        row = int(which - 1) // 3
        col = int(which - 1) % 3
        self.offset_x += int(col * self.width // 3)
        self.offset_y += int(row * self.height // 3)
        self.width //= 3
        self.height //= 3
        ctrl.mouse_move(*mg.pos())
        self.count += 1
        if self.count >= 4:
            self.reset(None)

    def pos(self):
        return self.offset_x + self.width/2, self.offset_y + self.height/2

    def reset(self, _):
        self.save_state()
        self.count = 0
        self.offset_x = 0
        self.offset_y = 0
        self.main_screen = ui.main_screen()
        self.width = self.main_screen.width
        self.height = self.main_screen.height

    def save_state(self):
        self.states.append((self.offset_x, self.offset_y, self.width, self.height))

    def go_back(self, _):
        last_state = self.states.pop()
        self.offset_x, self.offset_y, self.width, self.height = last_state
        self.count -= 1


def narrow(m):
    for d in m["mouseSnapNine.digits"]:
        mg.narrow(int(d))


digits = dict((str(n), n) for n in range(1, 11))

mg = MouseSnapNine()
group = ContextGroup("snapNine")
ctx = Context("mouseSnapNine", group=group)
keymap = {
    "{mouseSnapNine.digits}+": narrow,
    "(oops | back)": mg.go_back,
    "(reset | clear | escape)": mg.reset,
    "done": [mg.stop, lambda _: ctx.unload(), lambda _: speech.set_enabled(True)],
}
keymap.update({k: [v, mg.reset] for k, v in click_keymap.items()})
ctx.keymap(keymap)
ctx.set_list("digits", digits.keys())
group.load()
ctx.unload()

startCtx = Context("mouseSnapNineStarter")
startCtx.keymap({
    "snap": [mg.reset, mg.start, lambda _: ctx.load(), lambda _: speech.set_enabled(False)],
    # "snap done": [mg.stop, lambda _: ctx.unload()],
})
#mg.start()
# Hot reload while grid is active is very confusing without this.
speech.set_enabled(True)