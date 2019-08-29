# Tweaked eye_mon_snap.py with assumptions:
# - Three monitors, going left to right as #2 #1 #3
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
            main.x - 10 < p.x < main.x + main.width + 10
            and main.y - 10 < p.y < main.y + main.height + 10
    )


class MonThreeSnap:
    def __init__(self):
        if len(ui.screens()) == 1:
            return
        tap.register(tap.MMOVE, self.on_move)
        tap.register(tap.MCLICK, self.on_click)
        tracker.register("gaze", self.on_gaze)
        self.left = None
        self.right = None
        if len(ui.screens()) >= 2:
            print("Have left screen")
            self.left = ui.screens()[1]
            self.saved_mouse_left = Point2d(
                self.left.x + self.left.width // 2, self.left.y + self.left.height // 2
            )
        if len(ui.screens()) == 3:
            print("Have right screen")
            self.right = ui.screens()[2]
            self.saved_mouse_right = Point2d(
                self.right.x + self.right.width // 2, self.right.y + self.right.height // 2
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
        pos = mouse.xy_hist[-1]
        if self.right is None or (pos.x < main.width / 2 and self.left is not None):
            # print(f"Restore left: {pos} {self.saved_mouse_left}")
            if self.saved_mouse_left:
                mouse.last_ctrl = self.saved_mouse_left
                ctrl.mouse(self.saved_mouse_left.x, self.saved_mouse_left.y)
                # self.saved_mouse_left = None
                self.main_gaze = False
        elif pos.x > main.width / 2:
            # print(f"Restore right: {pos} {self.saved_mouse_right}")
            if self.saved_mouse_right:
                mouse.last_ctrl = self.saved_mouse_right
                ctrl.mouse(self.saved_mouse_right.x, self.saved_mouse_right.y)
                # self.saved_mouse_right = None
                self.main_gaze = False
        # else:
        #     print(f"Restore? {p}")

    def on_move(self, typ, e):
        if typ != tap.MMOVE:
            return
        p = Point2d(e.x, e.y)
        on_main = is_on_main(p)
        self.main_mouse = on_main

    def on_click(self, typ, e):
        # print(typ, e.flags & tap.UP)
        if e.flags & tap.UP:
            p = Point2d(e.x, e.y)
            # print(f"Checking for left/right saved update {p}")
            if self.right is None or (p.x < main.x and self.left is not None):
                # print("Updated left")
                self.saved_mouse_left = p
            elif p.x > main.x + 30 and self.right is not None:
                # print("Updated right")
                self.saved_mouse_right = p

# snap = MonThreeSnap()
