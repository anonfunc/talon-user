from talon import canvas, ctrl, ui, tap, cron
from talon.audio import noise
from talon.voice import Context, ContextGroup, Key
from talon_plugins import speech
from talon.track.geom import Point2d
from talon.track.filter import Acceleration

import time
from math import radians, pi, sin, cos

SIZE = 10
SPEED = 0.5


class MouseSonar:
    def __init__(self):
        self.main_screen = ui.main_screen()
        self.center_x = self.main_screen.x + self.main_screen.width // 2
        self.center_y = self.main_screen.y + self.main_screen.height // 2
        self.offset_x = self.center_x
        self.offset_y = self.center_y
        self.first_hiss = True
        self.hiss_job = None
        self.angle = 0
        self.radius = 15
        self.mcanvas = canvas.Canvas.from_screen(self.main_screen)
        self.active = False
        self.last_draw = time.time()
        self.accel = Acceleration(
            cd=(0.001, 100.0), v=(0.0004, 0.0025), lmb=1000.0, ratio=0.3
        )
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
        self.mcanvas.register("draw", self.draw)
        self.active = True
        ctrl.cursor_visible(False)

    def stop(self, *_):
        self.mcanvas.unregister("draw", self.draw)
        self.active = False
        ctrl.cursor_visible(True)

    def draw(self, canvas):
        paint = canvas.paint
        paint.color = "ff00ff"
        paint.stroke_width = 5
        # print(paint.__dir__())
        now = time.time()
        pos = Point2d(self.radius, 0)
        pos.rot(self.angle)

        ctrl.mouse_move(pos.x, pos.y)
        canvas.draw_line(self.center_x, self.center_y, pos.x, pos.y)
        self.last_draw = now

    def on_noise(self, noise):
        if not self.active:
            return
        print("NOIZE", noise)
        if noise == "pop":
            pass
        elif noise == "hiss_start":
            print("HISSING")
            if self.first_hiss:
                self.hiss_job = cron.interval("30ms", self.spin)
            else:
                self.hiss_job = cron.interval("30ms", self.drive)

            self.speed = SPEED
        elif noise == "hiss_end":
            print("NO LONGER HISSING")
            cron.cancel(self.hiss_job)
            self.hiss_job = None


    def spin(self):
        self.angle += radians(1)

    def drive(self):
        self.radius += 10

    def reset(self, _):
        self.offset_x = self.center_x
        self.offset_y = self.center_y
        self.first_hiss = True
        ctrl.cursor_visible(True)




# mg.start(None)
