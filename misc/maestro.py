from talon import applescript
from talon.voice import Context


def kmaestro(script_id):
    def _kmaestro(*_):
        print("Kmaestro {}".format(script_id))

        applescript.run(
            """
        tell application "Keyboard Maestro Engine"
            do script "{id}"
        end tell
        """.format(
                id=script_id
            )
        )

    return _kmaestro


ctx = Context("window")
ctx.keymap({"switcher": kmaestro("Switcher")})
