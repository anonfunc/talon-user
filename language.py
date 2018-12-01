from talon.voice import Context

def ExtensionContext(ext):
    def language_match(app, win):
        title = win.title
        #print("Window title:" + title)
        if app.bundle == 'com.microsoft.VSCode':
            filename = title.split(' - ', 1)[0]
        elif app.bundle == 'com.apple.Terminal':
            parts = title.split(' \u2014 ')
            if len(parts) >= 2 and parts[1].startswith(('vi ', 'vim ')):
                filename = parts[1].split(' ', 1)[1]
            else: return False 
        elif win.doc:
            filename = win.doc
        else: return False
        filename = filename.strip()
        return filename.endswith(ext)
    return language_match

ctx = Context('python', func=ExtensionContext('.py'))
ctx.keymap({'language test': 'python'})

ctx = Context('golang', func=ExtensionContext('.go'))
ctx.keymap({'language test': 'go'})

