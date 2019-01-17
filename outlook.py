from talon.voice import Context, Key

ctx = Context("outlook", bundle="com.microsoft.Outlook")
ctx.keymap({"archive": Key("ctrl+e")})
