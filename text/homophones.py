# https://raw.githubusercontent.com/dwiel/talon_community/master/text/homophones.py

import os

from talon import app, clip, cron
from talon.voice import Context, Str, press
from talon.webview import Webview

from .. import utils
from ..misc.popups import popup_template, list_template, dict_to_html

########################################################################
# global settings
########################################################################

# a list of homophones where each line is a comma separated list
# e.g. where,wear,ware
# a suitable one can be found here:
# https://github.com/pimentel/homophones
cwd = os.path.dirname(os.path.realpath(__file__))
homophones_file = os.path.join(cwd, "homophones.csv")
# if quick_replace, then when a word is selected and only one homophone exists,
# replace it without bringing up the options
quick_replace = True
########################################################################

context = Context("homophones")
pick_context = Context("pick")

phones = {}
canonical = []
with open(homophones_file, "r") as f:
    for h in f:
        # Skip comments and empty lines.
        if h.startswith("#") or not h.strip():
            continue
        h = h.rstrip()
        h = h.split(",")
        canonical.append(max(h, key=len))
        for w in h:
            w = w.lower()
            others = phones.get(w, None)
            if others is None:
                phones[w] = sorted(h)
            else:
                # if there are multiple hits, collapse them into one list
                others += h
                others = set(others)
                others = sorted(others)
                phones[w] = others

all_homophones = phones
active_word_list = None
is_selection = False

webview = Webview()

phones_template = popup_template + list_template("homophones")


def close_homophones():
    webview.hide()
    pick_context.unload()


def make_selection(m, is_selection, transform=lambda x: x):
    cron.after("0s", close_homophones)
    words = m._words
    d = None
    if len(words) == 1:
        d = int(utils.parse_word(words[0]))
    else:
        d = int(utils.parse_word(words[1]))
    w = active_word_list[d - 1]
    if len(words) > 1:
        w = transform(w)
    if is_selection:
        clip.set(w)
        press("cmd-v", wait=0)
    else:
        utils.insert(w)


def get_selection():
    with clip.capture() as s:
        press("cmd-c", wait=0)
    return s.get()


def raise_homophones(m, force_raise=False, is_selection=False):
    global pick_context
    global active_word_list

    if is_selection:
        word = get_selection()
        word = word.strip()
    # elif hasattr(m, "dgndictation"):
    #     # this mode is currently disabled...
    #     # experimenting with using a canonical representation and not using
    #     # dgndictation
    #     word = str(m.dgndictation[0]._words[0])
    #     word = parse_word(word)
    elif len(m._words) >= 2:
        word = str(m._words[len(m._words) - 1])
        word = utils.parse_word(word)

    word = word.lower()

    if word not in all_homophones:
        app.notify("homophones.py", '"%s" not in homophones list' % word)
        return

    active_word_list = all_homophones[word]
    if (
        is_selection
        and len(active_word_list) == 2
        and quick_replace
        and not force_raise
    ):
        if word == active_word_list[0].lower():
            new = active_word_list[1]
        else:
            new = active_word_list[0]
        clip.set(new)
        press("cmd-v", wait=0)
        return

    valid_indices = range(len(active_word_list))

    webview.render(phones_template, homophones=active_word_list)
    webview.show()

    keymap = {"(cancel | 0)": lambda x: close_homophones()}

    def capitalize(x):
        return x[0].upper() + x[1:]

    def uppercase(x):
        return x.upper()

    def lowercase(x):
        return x.lower()

    keymap.update(
        {
            "[pick] %s" % (i + 1): lambda m: make_selection(m, is_selection)
            for i in valid_indices
        }
    )
    keymap.update(
        {
            "(ship | title) %s"
            % (i + 1): lambda m: make_selection(m, is_selection, capitalize)
            for i in valid_indices
        }
    )
    keymap.update(
        {
            "(yeller | upper | uppercase) %s"
            % (i + 1): lambda m: make_selection(m, is_selection, uppercase)
            for i in valid_indices
        }
    )
    keymap.update(
        {
            "(lower | lowercase) %s"
            % (i + 1): lambda m: make_selection(m, is_selection, lowercase)
            for i in valid_indices
        }
    )
    pick_context.keymap(keymap)
    pick_context.load()


help_data = {
    "phones": "look up homophones for selected text",
    "phones [word]": "look up homophones for a given word",
    "pick [number]": "make a selection from the homophone list",
    "ship [number]": "make a selection and capitalize it",
    "yeller [number]": "make a selection and uppercase it",
    "lower [number]": "make a selection and lowercase it",
}

help_template = popup_template + dict_to_html("homophones help", help_data)


def homophones_help(m):
    webview.render(help_template)
    webview.show()

    keymap = {"(cancel | exit)": lambda x: close_homophones()}
    pick_context.keymap(keymap)
    pick_context.load()


context.keymap(
    {
        "(phones | homophones) help": homophones_help,
        "phones {homophones.canonical}": raise_homophones,
        "phones": lambda m: raise_homophones(m, is_selection=True),
        "force phones {homophones.canonical}": lambda m: raise_homophones(
            m, force_raise=True
        ),
        "force phones": lambda m: raise_homophones(
            m, force_raise=True, is_selection=True
        ),
    }
)
context.set_list("canonical", canonical)
