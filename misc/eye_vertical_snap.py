# Tweaked eye_mon_snap.py with assumptions:
# - Two monitors, going top to bottom as #2 #1
#
# Problems:
# - Gaze doesn't seem to do well with the edges of the screen.
#   You'll have to put your monitors farther apart than you might want from an ergonomic perspective.

from talon.track.geom import EyeFrame, Point2d
from talon_plugins.eye_mouse import config, mouse, tracker

from talon import ctrl, tap, ui

main = ui.main_screen()


def is_on_main(p):
    # Fudging this a bit around the edges
    return (
            main.x  < p.x < main.x + main.width
            and main.y - 5 < p.y < main.y + main.height + 5
    )


class MonTopSnap:
    def __init__(self):
        if len(ui.screens()) == 1:
            return
        tap.register(tap.MMOVE, self.on_move)
        tracker.register("gaze", self.on_gaze)
        self.top = None

        if len(ui.screens()) >= 2:
            print("Have top screen")
            self.top = ui.screens()[1]
            self.saved_mouse_top = Point2d(
                self.top.x + self.top.width // 2, self.top.y + self.top.height // 2
            )
        self.main_mouse = False
        self.main_gaze = False
        self.restore_counter = 0

    def on_gaze(self, b):
        if not config.control_mouse:
            return
        l, r = EyeFrame(b, "Left"), EyeFrame(b, "Right")
        p = (l.gaze + r.gaze) / 2
        # XXX Calculate avg. z-depth in calibration.
        # print(f"{(l.pos.z + r.pos.z) / 2}")
        main_gaze = -0.02 < p.x < 1.00 and -0.02 < p.y < 1.02 and bool(l or r)
        if self.main_gaze and self.main_mouse and not main_gaze:
            self.restore_counter += 1
            if self.restore_counter > 5:
                # print(bool(l), bool(r), p.x, p.y)
                self.restore()
        else:
            self.restore_counter = 0
            self.main_gaze = main_gaze
            # config.control_mouse = True

    def restore(self):
        # l, r = mouse.eye_hist[-1]
        # print(f"{(l.pos.z + r.pos.z) / 2}")
        ctrl.cursor_visible(True)

        if self.top is not None:
            # print(f"Restore left: {pos} {self.saved_mouse_left}")
            if self.saved_mouse_top:
                mouse.last_ctrl = self.saved_mouse_top
                ctrl.mouse(self.saved_mouse_top.x, self.saved_mouse_top.y)
                # self.saved_mouse_left = None
                self.main_gaze = False

        # else:
        #     print(f"Restore? {p}")

    def on_move(self, typ, e):
        if typ != tap.MMOVE:
            return
        p = Point2d(e.x, e.y)
        on_main = is_on_main(p)
        self.main_mouse = on_main
        if not on_main:
            self.saved_mouse_top = p


snap = MonTopSnap()
