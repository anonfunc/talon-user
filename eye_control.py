try:
    import eye
except:
    import eye_mouse as eye

from talon.voice import Word, Context, Key, Rep, Str, press

ctx = Context("eye_control")
ctx.keymap(
    {
        "debug overlay": lambda m: eye.on_menu("Eye Tracking >> Show Debug Overlay"),
        "control mouse": lambda m: eye.on_menu("Eye Tracking >> Control Mouse"),
        "camera overlay": lambda m: eye.on_menu("Eye Tracking >> Show Camera Overlay"),
        "run calibration": lambda m: eye.on_menu("Eye Tracking >> Calibrate"),
    }
)

try:
    eye.on_menu("Eye Tracking >> Control Mouse")
except:
    pass
