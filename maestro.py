from talon.voice import Context

from talon import applescript


def kmaestro(id):

    def _kmaestro(*_):
        print("Kmaestro {}".format(id))

        applescript.run(
            """
        tell application "Keyboard Maestro Engine"
            do script "{id}"
        end tell
        """.format(
                id=id
            )
        )

    return _kmaestro


keymap = {}
keymap.update(
    {
        "switcher": kmaestro("Switcher"),
        "window left": kmaestro("Windy Left"),
        "window right": kmaestro("Windy Right"),
        "window max": kmaestro("Windy Max"),
    }
)
ctx = Context("window")
ctx.keymap(keymap)
