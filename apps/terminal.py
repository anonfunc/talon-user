# Terminal context with smart directory navigation.
# Needs iterm2 shell integration for consistent navigation.
# See https://iterm2.com/documentation-shell-integration.html
# To update available directories on tab changes, `list` again.


import os
import re
import string
import subprocess

import talon.clip as clip
from talon import applescript, ui, tap, cron
from talon.voice import Context, Key, Str, press

from .. import utils
from ..misc.basic_keys import alphabet, alpha_alt
from ..misc.mouse import delayed_click
from ..text.formatters import LOWSMASH, DASH_SEPARATED, formatted_text

ctx = Context("terminal", bundle="com.googlecode.iterm2")
ctx.vocab = ["docker", "talon"]
ctx.vocab_remove = ["doctor", "Doctor", "talent", "talented"]

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
files = {}

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


to_alphabet_map = dict(zip(string.ascii_lowercase, alpha_alt))


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = re.sub(r"[.]", " ", value).strip().lower()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[-\s]+", " ", value)
    words = []
    for word in value.split():
        vowels = 0
        for c in "aeiou":
            vowels += word.count(c)
        if vowels == 0:
            word = " ".join([to_alphabet_map.get(c, c) for c in word])
        words.append(word)
    return " ".join(words)


def update_ctx(_=None, newdir=None):
    global ctx, subdirs, files
    cwd = current_dir()
    if newdir:
        cwd = os.path.join(cwd, newdir)
    subdirs = {
        slugify(c): c for c in os.listdir(cwd) if os.path.isdir(os.path.join(cwd, c))
    }
    files = {
        slugify(c): c
        for c in os.listdir(cwd)
        if not os.path.isdir(os.path.join(cwd, c))
    }
    subdirs[""] = ""
    ctx.set_list("subdirs", subdirs.keys())
    ctx.set_list("files", files.keys())
    # print(cwd, newdir, sorted(files.keys()), sorted(subdirs.keys()))
    if os.path.isdir(os.path.join(cwd, ".git")):
        branches = subprocess.check_output(
            ["git", "branch", "-l", "--format=%(refname:short)"], cwd=cwd
        )
        ctx.set_list("git-branches", branches)


def filename(m):
    # print("{}".format(" ".join([str(w) for w in m._words])))
    if len(m["terminal.files"]) >= 1:
        name = m["terminal.files"][0]
        utils.insert(f'"{files.get(name, "")}"')


def dirname(m):
    # print("{}".format(" ".join([str(w) for w in m._words])))
    try:
        if len(m["terminal.subdirs"]) >= 1:
            name = m["terminal.subdirs"][0]
            utils.insert(f'"{subdirs.get(name, "")}"')
    except KeyError:
        pass


def change_dir(m):
    # print("{}".format(" ".join([str(w) for w in m._words])))
    try:
        name = m["terminal.subdirs"][0]
        if name in subdirs:
            utils.insert(f"cd {subdirs[name]}; ls\n")
            update_ctx(newdir=subdirs[name])
    except KeyError:
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
        "cd {terminal.subdirs}": change_dir,
        "file {terminal.files}": filename,
        "(directory | folder) {terminal.subdirs}": dirname,
        "list": list_dir,
        "refresh": update_ctx,
        "clear terminal": Key("ctrl-l"),
        "go parent": parent,
        "go home": ["cd \n", update_ctx],
        "make (directory | folder) [<dgndictation>] [over]": [
            utils.i("mkdir -p "),
            formatted_text(LOWSMASH),
            update_ctx,
        ],
        "remove ": utils.i("rm "),
        "remove (directory | folder) [{terminal.subdirs}]": [
            utils.i("rm -rf "),
            dirname,
        ],
        "scroll down": [Key("shift-pagedown")],
        "scroll up": [Key("shift-pageup")],
        # "make [<dgndictation>]": ["make ", utils.text],
        # "mage [<dgndictation>]": ["mage -v ", utils.text],
        # git
        "jet [<dgndictation>]": ["git ", utils.text],
        "jet add": [utils.i("git add ")],
        "jet add all": [utils.i("git add .\n")],
        "jet branch": "git br\n",
        "jet clone": [utils.i("git clone ")],
        "jet checkout master": "git checkout master\n",
        # "jet checkout [<dgndictation>]": ["git checkout ", utils.text],
        "jet checkout {terminal.git-branches}": [
            "git checkout ",
            utils.list_value("terminal.git-branches"),
        ],
        "jet commit [<dgndictation>]": ["git commit ", utils.text],
        "jet commit all [<dgndictation>]": [
            'git commit -a -m ""',
            Key("left"),
            utils.text,
        ],
        "jet amend all head": [utils.i("git commit --amend -a -C HEAD")],
        "jet amend": [utils.i("git commit --amend ")],
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
        "dash {terminal.alphabet}": [" -", letter, " "],
        "dash dash <dgndictation> [over]": [" --", formatted_text(DASH_SEPARATED), " "],
        "dash <dgndictation> [over]": [" -", formatted_text(DASH_SEPARATED), " "],
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
        "clear line": [Key("end"), Key("shift-home"), extendable("backspace")],
        "clear left": extendable("backspace"),
        "clear right": extendable("delete"),
        "clear word left": extendable("alt-backspace"),
        "clear word right": extendable("alt-delete"),
        "clear way left": extendable("shift-home delete"),
        "clear way right": extendable("shift-end delete"),
        # searching
        "search [<dgndictation>]": [Key("cmd-f"), utils.text],
        # clipboard
        "cut this": Key("cmd-x"),
        "copy this": Key("cmd-c"),
        "paste [here]": Key("cmd-v"),
        # Copying
        "copy path": lambda _: clip.set(current_dir()),
        "copy phrase": [utils.select_last_insert, Key("cmd-c")],
        "copy all": [Key("cmd-a cmd-c")],
        "copy line": extendable("cmd-left cmd-left cmd-shift-right cmd-c cmd-right"),
        "copy word left": extendable("shift-alt-left cmd-c"),
        "copy word right": extendable("shift-alt-right cmd-c"),
        "copy way left": extendable("cmd-shift-left cmd-c"),
        "copy way right": extendable("cmd-shift-right cmd-c"),
        "copy way up": extendable("cmd-shift-up cmd-c"),
        "copy way down": extendable("cmd-shift-down cmd-c"),
        # Cutting
        "cut phrase": [utils.select_last_insert, Key("cmd-x")],
        "cut all": [Key("cmd-a cmd-x")],
        "cut line": extendable("cmd-left cmd-left cmd-shift-right cmd-x cmd-right"),
        "cut word left": extendable("shift-alt-left cmd-x"),
        "cut word right": extendable("shift-alt-right cmd-x"),
        "cut way left": extendable("cmd-shift-left cmd-x"),
        "cut way right": extendable("cmd-shift-right cmd-x"),
        "cut way up": extendable("cmd-shift-up cmd-x"),
        "cut way down": extendable("cmd-shift-down cmd-x"),
    }
)


def terminal_hotkey(_, e):
    """Adds an alt-w to pick up zle selection as well."""
    window = ui.active_window()
    bundle = window.app.bundle
    if bundle != "com.googlecode.iterm2":
        return
    if e == "cmd-c" and e.up:
        # print("intercept " + str(e))
        Key("alt-w")(None)
    elif e == "enter" and e.up:
        # print("intercept " + str(e))
        cron.after("500ms", lambda: update_ctx(None))
    return True


tap.register(tap.HOOK | tap.KEY, terminal_hotkey)

ctx.set_list("alphabet", alphabet.keys())
