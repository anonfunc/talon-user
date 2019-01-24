from talon import canvas, ctrl, ui
from talon.voice import Context, ContextGroup, Key
from talon.voice import talon as talon_cg
from talon_plugins import speech


class MouseSnap:
    def __init__(self):
        self.main_screen = ui.main_screen()
        self.offset_x = 0
        self.offset_y = 0
        self.width = self.main_screen.width
        self.height = self.main_screen.height
        self.save_last()
        self.mcanvas = canvas.Canvas.from_screen(self.main_screen)
        self.active = False

    def start(self, *_):
        if self.active:
            return
        self.mcanvas.register('draw', self.draw)
        self.active = True

    def stop(self, *_):
        if not self.active:
            return
        self.mcanvas.unregister('draw', self.draw)
        self.active = False

    def draw(self, canvas):
        paint = canvas.paint
        paint.color = "ff0000"
        canvas.draw_line(self.offset_x + self.width / 2, self.offset_y, self.offset_x + self.width / 2,
                         self.offset_y + self.height)
        canvas.draw_line(self.offset_x, self.offset_y + self.height / 2, self.offset_x + self.width,
                         self.offset_y + self.height / 2)

    def north(self, _):
        self.save_last()
        self.height /= 2

    def south(self, _):
        self.save_last()
        self.height /= 2
        self.offset_y += self.height

    def west(self, _):
        self.save_last()
        self.width /= 2

    def east(self, _):
        self.save_last()
        self.width /= 2
        self.offset_x += self.width

    def pos(self):
        return self.offset_x + self.width/2, self.offset_y + self.height/2

    def reset(self, _):
        self.save_last()
        self.offset_x = 0
        self.offset_y = 0
        self.width = self.main_screen.width
        self.height = self.main_screen.height

    def save_last(self):
        self.last_state = (self.offset_x, self.offset_y, self.width, self.height)

    def go_back(self, _):
        self.offset_x, self.offset_y, self.width, self.height = self.last_state


mg = MouseSnap()

group = ContextGroup("mouseSnap")
ctx = Context("mouseSnap", group=group)
ctx.keymap({
    "north": mg.north,
    "east": mg.east,
    "south": mg.south,
    "west": mg.west,
    "leap": [lambda _: ctrl.mouse(*mg.pos()), mg.stop, lambda _: group.unload()],
    "oops": mg.go_back,
    "done": [mg.stop, lambda _: group.unload()],
})

startCtx = Context("mouseSnapStarter")
startCtx.keymap({
    "mouse snap": [mg.start, lambda _: group.load()],
    "mouse done": [mg.stop, lambda _: group.unload()],
})
