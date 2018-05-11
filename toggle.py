try:
    from talon import app, voice
    from talon.api import lib

    def set_enabled(enable):
        if enable:
            voice.talon.enable()
            app.icon_color(0, 0.7, 0, 1)
        else:
            voice.talon.disable()
            app.icon_color(1, 0, 0, 1)
        lib.menu_check(b"!Enable Speech Recognition", enable)

    def on_menu(item):
        if item == "!Enable Speech Recognition":
            set_enabled(not voice.talon.enabled)

    app.register("menu", on_menu)
    set_enabled(voice.talon.enabled)
except:
    pass
