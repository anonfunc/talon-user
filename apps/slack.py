from talon.voice import Context, Key

from ..utils import text

ctx = Context("slack", bundle="com.tinyspeck.slackmacgap")
ctx.keymap(
    {
        "go jump": Key("cmd-k"),
        "go (dm's | direct messages | messages)": Key("cmd-shift-k"),
        "go (and read | unread)": Key("cmd-shift-a"),
        "go (threads | thread)": Key("cmd-shift-t"),
        "react [<dgndictation>]": [Key("cmd-shift-\\"), text],
        "toggle zoom": Key("cmd-."),
        "go last unread": Key("alt-shift-up"),
        "go next unread": Key("alt-shift-down"),
    }
)
