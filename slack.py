from talon.voice import Context, Key

from .utility import text

ctx = Context("slack", bundle="com.tinyspeck.slackmacgap")
ctx.keymap(
    {
        "jump": Key("cmd-k"),
        "(dm's | direct messages | messages)": Key("cmd-shift-k"),
        "(and read | unread)": Key("cmd-shift-a"),
        "(threads | all threads)": Key("cmd-shift-t"),
        "react [<dgndictation>]": [Key("cmd-shift-\\"), text],
        "zoom": Key("cmd-."),
        "next unread": Key("alt-shift-down"),
    }
)
