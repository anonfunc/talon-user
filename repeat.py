import talon
from talon.voice import Word, Context, Str, Rep

from user.utility import text_to_number, optional_numerals


def repeat(m):

    words = m._words

    repeat_count = text_to_number(words[1:])
    print("Repeat! {} {}".format([str(w) for w in words], repeat_count))
    if not repeat_count:
        repeat_count = 1
    repeater = Rep(repeat_count)
    repeater.ctx = m.ctx
    return repeater(None)


ctx = Context("repeaters")
ctx.keymap({"repeat" + optional_numerals: repeat})
