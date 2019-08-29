import time

from talon import ctrl, ui
from talon_plugins.eye_mouse import tracker, mouse, control_mouse, Point2d

main = ui.main_screen()


def is_on_main(p):
    # Fudging this a bit around the edges
    return (
        main.x - 10 < p.x < main.x + main.width + 10
        and main.y - 10 < p.y < main.y + main.height + 10
    )


class EyeHide:
    def __init__(self):
        self.show = False
        tracker.register("post:gaze", self.on_gaze)
        ui.register("win_focus", self.on_focus)
        ui.register("app_activate", self.on_focus)

    def on_focus(self, win):
        ctrl.cursor_visible(self.show or not control_mouse.enabled)

    def on_gaze(self, b):
        p = Point2d(*ctrl.mouse_pos())
        on_main = is_on_main(p)
        if not control_mouse.enabled or not on_main or (mouse.last_ctrl and mouse.break_force > 6):
            self.cursor(True)
            ctrl.cursor_visible(True)

        else:
            try:
                # hides after every eye jump until a head movement
                origin = mouse.origin
                frames = [xy for xy in mouse.xy_hist if xy.ts >= origin.ts]
                m = max([(origin - xy).len() for xy in frames])
                self.cursor(m > 5)

                return
                # this variant hides the cursor on every eye jump until it settles (can tweak radius up to 200)
                p, origin, radius = mouse.zone1
                self.cursor(radius > 20)
            except Exception:
                self.cursor(True)

    def cursor(self, show):
        now = time.time()
        if show:
            self.last_show = now
        elif self.show and now - self.last_show < 0.5:
            return

        if show != self.show:
            ctrl.cursor_visible(show)
            self.show = show


hide = EyeHide()
if not control_mouse.enabled:
    ctrl.cursor_visible(True)
