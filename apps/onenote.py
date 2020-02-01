from talon.voice import Context, Key

from .. import utils

ctx = Context("onenote", bundle="com.microsoft.onenote.mac")
ctx.keymap(
    {
        "sync notebook": Key("cmd+s"),
        "sync all notebooks": Key("shift+cmd+s"),
        "new page": Key("cmd+n"),
        "new section": Key("cmd+t"),
        "move page": Key("shift+cmd+m"),
        "copy page": Key("shift+cmd+c"),
        "make sub page": Key("alt+cmd+]"),
        "promote sub page": Key("alt+cmd+["),
        "go back": Key("ctrl+cmd+left"),
        "go forward": Key("ctrl+cmd+right"),
        "toggle ribbon": Key("alt+cmd+r"),
        "focus notifications": Key("alt+cmd+o"),
        # Zoom
        "zoom out": Key("cmd+="),
        "zoom in": Key("cmd+-"),
        "zoom clear": Key("cmd+0"),
        # Search
        "search [this]": Key("cmd+f"),
        "search for <dgndictation> [over]": [Key("cmd+f"), utils.delay(0.3), utils.text],
        "search all": Key("alt+cmd+f"),
        "search all for <dgndictation> [over]": [Key("alt+cmd+f"), utils.delay(0.3), utils.text],
        "go next result": Key("cmd+g"),
        "go last result": Key("shift+cmd+g"),
        # The universal command
        "please <dgndictation> [over]": [Key("shift+cmd+/"), utils.delay(0.3), utils.text],
        # TODO WYSIWYG commands

    }
)
