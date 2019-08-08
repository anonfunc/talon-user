from talon import canvas, ctrl, ui, tap
from talon.voice import Context, ContextGroup
from talon_plugins import speech, eye_mouse, eye_zoom_mouse

from .mouse import click_keymap


class MouseSnapSquid:
    def __init__(self):
        self.states = []
        self.main_screen = ui.main_screen()
        self.offset_x = self.main_screen.x
        self.offset_y = self.main_screen.y
        self.width = self.main_screen.width
        self.height = self.main_screen.height
        self.states.append((self.offset_x, self.offset_y, self.width, self.height))
        self.mcanvas = canvas.Canvas.from_screen(self.main_screen)
        self.active = False
        self.moving = False
        self.count = 0
        self.rows = 60
        self.cols = 55

    def start(self, *_):
        if self.active:
            return
        if eye_zoom_mouse.zoom_mouse.enabled:
            return
        if eye_mouse.control_mouse.enabled:
            return
        self.mcanvas.register('draw', self.draw)
        self.active = True

    def stop(self, *_):
        self.mcanvas.unregister('draw', self.draw)
        self.active = False

    def draw(self, canvas):
        paint = canvas.paint
        paint.color = "ff0000"
        # for i in range(1, self.cols+1):
        #     canvas.draw_line(self.offset_x + i * self.width // self.cols, self.offset_y, self.offset_x + i * self.width // self.cols,
        #                      self.offset_y + self.height)
        # for i in range(1, self.rows+1):
        #     canvas.draw_line(self.offset_x, self.offset_y + i * self.height // self.rows, self.offset_x + self.width,
        #                      self.offset_y + i * self.height // self.rows)

        for row in range(self.rows):
            for col in range(self.cols):
                canvas.draw_text(f"{row:02d}{col:02d}", self.offset_x + (col) * self.width//(self.cols),
                                 self.offset_y + (row+1) * self.height//(self.rows))

    def narrow(self, digits):
        self.save_state()
        # print(digits)
        row = int(digits[0]) * 10 + int(digits[1])
        col = int(digits[2]) * 10 + int(digits[3])
        # print(row, col)
        offset_x = self.offset_x + int(col * self.width // self.cols)
        offset_y = self.offset_y + int(row * self.height // self.rows)
        width = self.width // self.cols
        height = self.height // self.cols
        # print(offset_x + width//2, offset_y + height//2)
        ctrl.mouse_move(offset_x + width//2, offset_y + height//2)
        self.count += 1
        if self.count >= 2:
            self.reset(None)

    def reset(self, _):
        self.save_state()
        self.count = 0
        self.offset_x = self.main_screen.x
        self.offset_y = self.main_screen.y
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
    mg.narrow(m["mouseSnapSquid.digits"])


digits = dict((str(n), n) for n in range(0, 10))

mg = MouseSnapSquid()
group = ContextGroup("squid")
ctx = Context("mouseSnapSquid", group=group)
keymap = {
    "{mouseSnapSquid.digits}+": narrow,
    "squid": [mg.stop, lambda _: ctx.unload(), lambda _: speech.set_enabled(True)],
}
keymap.update({k: [v, mg.reset] for k, v in click_keymap.items()})
ctx.keymap(keymap)
ctx.set_list("digits", digits.keys())
group.load()
ctx.unload()

startCtx = Context("mouseSnapSquidStarter")
startCtx.keymap({
    "squid": [mg.reset, mg.start, lambda _: ctx.load(), lambda _: speech.set_enabled(False)],
    # "snap done": [mg.stop, lambda _: ctx.unload()],
})
# mg.start()
# Hot reload while grid is active is very confusing without this.
speech.set_enabled(True)