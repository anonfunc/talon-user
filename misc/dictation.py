from talon.voice import ContextGroup, Context, Key
from talon import ui

from ..utils import insert, parse_word

# used for auto-spacing
punctuation = set(".,-!?")
sentence_ends = set(".!?").union({"\n", "\n\n"})


class AutoFormat:
    def __init__(self):
        self.reset()
        self.caps = True
        self.space = False
        ui.register("app_deactivate", lambda app: self.reset())
        ui.register("win_focus", lambda win: self.reset())

    def reset(self):
        self.caps = True
        self.space = False

    def insert_word(self, word):
        word = parse_word(word)

        if self.caps:
            word = word[0].upper() + word[1:]
        if self.space and word[0] not in punctuation and "\n" not in word:
            insert(" ")

        insert(word)

        self.caps = word in sentence_ends
        self.space = "\n" not in word

    def phrase(self, m):
        for word in m.dgndictation[0]:
            self.insert_word(word)


dictation_group = ContextGroup("dictation")
dictation = Context("dictation", group=dictation_group)
dictation_group.load()
dictation_group.disable()

auto_format = AutoFormat()
dictation.keymap({"<dgndictation> [over]": auto_format.phrase, "press enter": Key("enter")})
