from talon import canvas, ctrl, ui
from talon.audio import noise
from talon.voice import Context, ContextGroup, Key
from talon_plugins import speech

import time
from math import radians, pi, sin, cos

SIZE = 10
SPEED = 300


class MouseRcCar:
    def __init__(self):
        self.main_screen = ui.main_screen()
        self.offset_x = self.main_screen.width // 2
        self.offset_y = self.main_screen.height // 2
        self.angle = 0
        self.speed = 0
        self.mcanvas = canvas.Canvas.from_screen(self.main_screen)
        self.active = False
        self.last_draw = time.time()
        noise.register("noise", self.on_noise)

    def start(self, *_):
        if self.active:
            return
        self.mcanvas.register('draw', self.draw)
        self.active = True
        ctrl.cursor_visible(False)

    def stop(self, *_):
        self.mcanvas.unregister('draw', self.draw)
        self.active = False
        ctrl.cursor_visible(True)

    def draw(self, canvas):
        paint = canvas.paint
        paint.color = "ff00ff"
        paint.stroke_width = 5
        # print(paint.__dir__())
        elapsed = time.time() - self.last_draw
        c = cos(self.angle)
        s = sin(self.angle)
        dx = elapsed*self.speed * c
        dy = elapsed*self.speed * s
        self.offset_x += dx
        self.offset_y += dy
        ctrl.mouse_move(self.offset_x, self.offset_y)
        line1 = self.rotate(c, s, 0, 0, -2*SIZE, SIZE)
        line2 = self.rotate(c, s, 0, 0, -2*SIZE, -SIZE)
        line3 = (line1[2], line1[3], line2[2], line2[3])

        canvas.draw_line(self.offset_x + line1[0], self.offset_y+line1[1], self.offset_x+line1[2],self.offset_y+line1[3])
        canvas.draw_line(self.offset_x + line2[0], self.offset_y+line2[1], self.offset_x+line2[2],self.offset_y+line2[3])
        canvas.draw_line(self.offset_x + line3[0], self.offset_y+line3[1], self.offset_x+line3[2],self.offset_y+line3[3])
        self.last_draw = time.time()

    def rotate(self, c, s, x1, y1, x2, y2):
        return x1*c+y1*s, x1*s-y1*c, x2*c+y2*s, x2*s-y2*c

    def on_noise(self, noise):
        if not self.active:
            return
        # print("NOIZE", noise)
        if noise == "pop":
            self.angle -= radians(90)
            if self.angle <= 0:
                self.angle += 2*pi
        elif noise == "hiss_start":
            self.speed = SPEED
        elif noise == "hiss_end":
            self.speed = 0

    def pos(self):
        return self.offset_x + self.width/2, self.offset_y + self.height/2

    def reset(self, _):
        self.offset_x = self.main_screen.width // 2
        self.offset_y = self.main_screen.height // 2
        self.angle = 0
        self.speed = 0
        self.main_screen = ui.main_screen()
        ctrl.cursor_visible(True)


# mg = MouseRcCar()
# ctx = Context("MouseRcCarStarter")
# ctx.keymap({
#     "start driving": [mg.reset, mg.start],
#     "(done | stop) driving": mg.stop,
#     # "snap done": [mg.stop, lambda _: ctx.unload()],
# })

#mg.start(None)
