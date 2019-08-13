# Terminal context with smart directory navigation.
# Needs iterm2 shell integration for consistent navigation.
# See https://iterm2.com/documentation-shell-integration.html
# To update available directories on tab changes, `list` again.


import os
import re

import talon.clip as clip
from talon import applescript
from talon.voice import Context, Key, Str, press

from .. import utils
from ..misc.basic_keys import alphabet
from ..misc.mouse import delayed_click

ctx = Context("terminal", bundle="com.googlecode.iterm2")
ctx.vocab = ["docker", "talon"]
ctx.vocab_remove = ["doctor", "Doctor"]


try:
    from ..text.homophones import all_homophones

    # Map from every homophone back to the row it was in.
    homophone_lookup = {
        item.lower(): words for canon, words in all_homophones.items() for item in words
    }
except ImportError:
    homophone_lookup = {"right": ["right", "write"], "write": ["right", "write"]}
    all_homophones = homophone_lookup.keys()


subdirs = {}

extension = None


def extendable(d):
    def wrapper(m):
        global extension
        extension = Key(d)
        extension(m)

    return wrapper


def set_extension(d):
    def wrapper(_):
        global extension
        extension = d

    return wrapper


def do_extension(m):
    # noinspection PyProtectedMember
    count = max(utils.text_to_number([utils.parse_word(w) for w in m._words[1:]]), 1)
    for _ in range(count):
        extension(m)


# jcooper-korg from talon slack
def select_text_to_left_of_cursor(m):
    words = utils.parse_words(m)
    if not words:
        return
    key = utils.join_words(words).lower()
    keys = homophone_lookup.get(key, [key])
    press("left", wait=2000)
    press("right", wait=2000)
    press("shift-home", wait=2000)
    with clip.capture() as s:
        press("alt-w", wait=2000)
    press("right", wait=2000)
    text_left = s.get()
    result = -1
    for needle in keys:
        find = text_left.find(needle)
        if find > result:
            result = find
            key = needle
            break

    # print(text_left, keys, result)
    if result == -1:
        return
    # cursor over to the found key text
    for i in range(0, len(text_left) - result):
        press("left", wait=0)
    # now select the matching key text
    for i in range(0, len(key)):
        press("shift-right")
    set_extension(lambda _: select_text_to_left_of_cursor(m))


# jcooper-korg from talon slack
def select_text_to_right_of_cursor(m):
    words = utils.parse_words(m)
    if not words:
        return
    key = utils.join_words(words).lower()
    keys = homophone_lookup.get(key, [key])
    press("right", wait=2000)
    press("left", wait=2000)
    press("shift-end", wait=2000)
    with clip.capture() as s:
        press("alt-w", wait=2000)
    text_right = s.get()
    press("left", wait=2000)
    result = len(text_right) + 1
    for needle in keys:
        index = text_right.find(needle)
        if index == -1:
            continue
        if index < result:
            result = index
            key = needle
            break

    # print(text_right, keys, result, len(text_right) + 1)
    if result == len(text_right) + 1:
        return
    # cursor over to the found key text
    for i in range(0, result):
        press("right", wait=0)
    # now select the matching key text
    for i in range(0, len(key)):
        press("shift-right")
    set_extension(lambda _: select_text_to_right_of_cursor(m))


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = re.sub("[^\w\s-]", "", value).strip().lower()
    value = re.sub("[-\s]+", " ", value)
    return value


def update_ctx(_=None, newdir=None):
    global ctx, subdirs
    cwd = current_dir()
    if newdir:
        cwd = os.path.join(cwd, newdir)
    subdirs = {
        slugify(c): c for c in os.listdir(cwd) if os.path.isdir(os.path.join(cwd, c))
    }
    subdirs[""] = ""
    ctx.set_list("subdirs", subdirs.keys())
    print(cwd, newdir)


def change_dir(m):
    # print("{}".format(" ".join([str(w) for w in m._words])))
    name = None
    if len(m._words) > 1:
        name = utils.parse_word(m._words[1])
    if name in subdirs:
        utils.insert("cd {}; ls\n".format(subdirs[name]))
        update_ctx(newdir=subdirs[name])
    else:
        utils.insert("cd ")


def list_dir(_):
    utils.insert("ls\n")
    update_ctx()


def current_dir():
    return applescript.run(
        """
        tell application "iTerm"
            tell current session of current window
                variable named "session.path"
            end tell
        end tell
        """
    )


def parent(_):
    utils.insert("cd ..; ls\n")
    update_ctx(newdir="..")


def home(_):
    utils.insert("cd ..; ls\n")
    update_ctx(newdir=os.path.expanduser("~"))


def grab_change_directory(m):
    old_clip = clip.get()
    new_dir = None
    cwd = current_dir()
    try:
        delayed_click(m, button=0, times=2)
        new_dir = clip.get()
    finally:
        clip.set(old_clip)

    if new_dir.startswith("/"):
        new_path = new_dir.strip("'")
    else:
        new_path = os.path.join(cwd, new_dir.strip("'"))

    if os.path.isdir(new_path):
        utils.insert("cd {}; ls\n".format(new_dir))
        update_ctx(newdir=new_dir)
    else:
        print("{} not in {}".format(new_dir, subdirs))


def grab_thing(m):
    old_clip = clip.get()
    try:
        delayed_click(m, button=0, times=2)
        delayed_click(m, button=2, times=1)  # Middle click?
    finally:
        clip.set(old_clip)


def letter(m):
    try:
        utils.insert([alphabet[k] for k in m["terminal.alphabet"]])
    except KeyError:
        pass


mapping = {"semicolon": ";", r"new-line": "\n", r"new-paragraph": "\n\n"}

ctx.keymap(
    {
        "(cd {terminal.subdirs} | cd)": change_dir,
        "list": list_dir,
        "clear terminal": Key("ctrl-l"),
        "go parent": parent,
        "go home": ["cd \n", update_ctx],
        "make dir": utils.i("mkdir -p "),
        "remove ": utils.i("rm "),
        "remove directory": utils.i("rm -rf "),
        "scroll down": [Key("shift-pagedown")],
        "scroll up": [Key("shift-pageup")],
        "make [<dgndictation>]": ["make ", utils.text],
        "mage [<dgndictation>]": ["mage -v ", utils.text],
        # git
        "jet [<dgndictation>]": ["git ", utils.text],
        "jet add": [utils.i("git add ")],
        "jet add all": [utils.i("git add .\n")],
        "jet branch": "git br\n",
        "jet clone": [utils.i("git clone ")],
        "jet checkout master": "git checkout master\n",
        "jet checkout [<dgndictation>]": ["git checkout ", utils.text],
        "jet commit [<dgndictation>]": ["git commit ", utils.text],
        "jet commit all [<dgndictation>]": ['git commit -a -m ""', Key("left"), utils.text],
        "jet amend all head": [utils.i('git commit --amend -a -C HEAD')],
        "jet amend": [utils.i('git commit --amend ')],
        "jet diff": "git diff\n",
        "jet history": "git hist\n",
        "jet merge [<dgndictation>]": ["git merge ", utils.text],
        "jet pull [<dgndictation>]": ["git pull ", utils.text],
        "jet pull (base | rebase | read [base]) [<dgndictation>]": [
            "git pull --rebase ",
            utils.text,
        ],
        "jet push [<dgndictation>]": ["git push ", utils.text],
        "jet reset": utils.i("git reset "),
        "jet rebase": utils.i("git rebase -i HEAD~"),
        "jet stash": "git stash\n",
        "jet status": "git status\n",
        "jet stat": "git status --short\n",
        "ref head": utils.i("HEAD"),
        "ref parent": utils.i("HEAD^"),
        # common
        "gradle": utils.i("./gradlew "),
        "gradle deploy": utils.i("./gradlew deploy"),
        "gradle build": utils.i("./gradlew deploy"),
        "activate": utils.i("act"),
        "grab": grab_thing,
        "follow": grab_change_directory,
        "jump [<dgndictation>]": ["zz ", utils.text, "\n"],
        # Options
        "dash {terminal.alphabet}": ["-", letter],
        "dash dash <dgnwords>": ["--", utils.word],
        "dash <dgnwords>": ["-", utils.word],

        # Editor commands
        # moving
        "go word left": extendable("alt-left"),
        "go word right": extendable("alt-right"),
        "go line start": extendable("ctrl-a"),
        "go line end": extendable("ctrl-e"),
        "go way left": extendable("ctrl-a"),
        "go way right": extendable("ctrl-e"),
        "go phrase left": [utils.select_last_insert, extendable("left")],
        # selecting
        "select all": [Key("home shift-end")],
        "(correct | select phrase)": utils.select_last_insert,
        "select last <dgndictation> [over]": select_text_to_left_of_cursor,
        "select next <dgndictation> [over]": select_text_to_right_of_cursor,
        "select line": Key("home shift-end"),
        "select left": extendable("shift-left"),
        "select right": extendable("shift-right"),
        "select up": extendable("shift-up"),
        "select down": extendable("shift-down"),
        "select word left": [
            Key("left shift-right left alt-left alt-right shift-alt-left"),
            set_extension(Key("shift-alt-left")),
        ],
        "select word right": [
            Key("right shift-left right alt-right alt-left shift-alt-right"),
            set_extension(Key("shift-alt-right")),
        ],
        f"extend {utils.optional_numerals}": do_extension,
        "select way left": extendable("shift-home"),
        "select way right": extendable("shift-end"),
        # deleting
        "clear phrase": [utils.select_last_insert, extendable("backspace")],
        "clear line": extendable("home shift-end backspace"),
        "clear left": extendable("backspace"),
        "clear right": extendable("delete"),
        "clear word left": extendable("alt-backspace"),
        "clear word right": extendable("alt-delete"),
        "clear way left": extendable("shift-home delete"),
        "clear way right": extendable("shift-end delete"),
        # searching
        "search [<dgndictation>]": [Key("cmd-f"), utils.text],
    }
)

ctx.set_list("alphabet", alphabet.keys())
