from talon.voice import Context, Key

from .. import utils


def pick(m):
    try:
        index = utils.ordinal_indexes[m["picker.ordinal"][0]]
        Key("down " * index + "enter")(m)
    except:
        pass


ctx = Context("picker")
ctx.keymap({"pick {picker.ordinal}": pick})

ctx.set_list("ordinal", utils.ordinal_indexes.keys())
