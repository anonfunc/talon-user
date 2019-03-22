from talon import canvas, ctrl, ui, tap
from talon.audio import noise
from talon.voice import Context, ContextGroup, Key
from talon_plugins import speech
from talon.track.geom import Point2d
from talon.track.filter import Acceleration

import time
from math import radians, pi, sin, cos

SIZE = 10
SPEED = .5


class MouseRcCar:
    def __init__(self):
        self.main_screen = ui.main_screen()
        self.offset_x = self.main_screen.x + self.main_screen.width // 2
        self.offset_y = self.main_screen.y + self.main_screen.height // 2
        self.angle = 0
        self.speed = 0.0
        self.mcanvas = canvas.Canvas.from_screen(self.main_screen)
        self.active = False
        self.last_draw = time.time()
        self.accel = Acceleration(
            cd=(.001, 100.0),
            v=(0.0004, 0.0025),
            lmb=1000.0,
            ratio=0.3
        )
        self.hiss_start = time.time()
        noise.register("noise", self.on_noise)
        # tap.register(tap.MMOVE, self.on_move)

    # def on_move(self, typ, e):
    #     if typ != tap.MMOVE or not self.active:
    #         return
    #
    #     # print("moved ", e, self.offset_x, self.offset_y)
    #     if (e.x, e.y) != (self.offset_x, self.offset_y):
    #         self.stop(None)

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
        now = time.time()
        elapsed = now - self.last_draw
        hiss_dt = now - self.hiss_start
        c = cos(self.angle)
        s = sin(self.angle)
        delta = Point2d(self.speed * c, self.speed * s)
        # print(delta)
        delta = delta.apply(self.accel, hiss_dt/100)
        # print(delta)
        self.offset_x += delta.x
        if self.offset_x < 0:
            self.offset_x = 0
        elif self.offset_x > self.main_screen.width:
            self.offset_x = self.main_screen.width
        self.offset_y += delta.y
        if self.offset_y < 0:
            self.offset_y = 0
        elif self.offset_y > self.main_screen.height:
            self.offset_y = self.main_screen.height
        ctrl.mouse_move(self.offset_x, self.offset_y)
        line1 = self.rotate(c, s, 0, 0, -2*SIZE, SIZE)
        line2 = self.rotate(c, s, 0, 0, -2*SIZE, -SIZE)
        line3 = (line1[2], line1[3], line2[2], line2[3])

        canvas.draw_line(self.offset_x + line1[0], self.offset_y+line1[1], self.offset_x+line1[2],self.offset_y+line1[3])
        canvas.draw_line(self.offset_x + line2[0], self.offset_y+line2[1], self.offset_x+line2[2],self.offset_y+line2[3])
        canvas.draw_line(self.offset_x + line3[0], self.offset_y+line3[1], self.offset_x+line3[2],self.offset_y+line3[3])
        self.last_draw = now

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
            self.hiss_start = time.time()
        elif noise == "hiss_end":
            self.speed = 0.0

    def reset(self, _):
        self.offset_x = self.main_screen.x + self.main_screen.width // 2
        self.offset_y = self.main_screen.y + self.main_screen.height // 2
        self.angle = 0
        self.speed = 0.0
        self.main_screen = ui.main_screen()
        ctrl.cursor_visible(True)

#
# mg = MouseRcCar()
# ctx = Context("MouseRcCarStarter")
# ctx.keymap({
#     "start driving": [mg.reset, mg.start],
#     "(done | stop) driving": mg.stop,
#     # "snap done": [mg.stop, lambda _: ctx.unload()],
# })
#
# #mg.start(None)
