# Terminal context with smart directory navigation.
# Needs iterm2 shell integration for consistent navigation.
# See https://iterm2.com/documentation-shell-integration.html
# To update available directories on tab changes, `list` again.


import os
import re
import subprocess
import time

from talon import applescript
from talon.api import ffi
from talon.voice import Key, press, Str, Context

ctx = Context("terminal", bundle="com.googlecode.iterm2")

subdirs = {}


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
    print("{}".format(" ".join([str(w) for w in m._words])))
    name = None
    if len(m._words) > 1:
        name = str(m._words[1])
    if name in subdirs:
        Str("cd {}; ls\n".format(subdirs[name]))(None)
        update_ctx(newdir=subdirs[name])
    else:
        Str("cd ")(None)


def list_dir(_):
    Str("ls\n")(None)
    update_ctx()


def current_dir():
    return ffi.string(
        applescript.run(
            """
    tell application "iTerm"
        tell current session of current window
            variable named "session.path"
        end tell
    end tell
    """
        )
    ).decode(
        "utf-8"
    )


def parent(_):
    Str("cd ..; ls\n")(None)
    update_ctx(newdir="..")


def home(_):
    Str("cd ..; ls\n")(None)
    update_ctx(newdir=os.path.expanduser("~"))


def text(m):
    try:
        tmp = [str(s).lower() for s in m.dgndictation[0]._words]
        words = [parse_word(word) for word in tmp]
        Str(" ".join(words))(None)
    except AttributeError:
        return


mapping = {"semicolon": ";", r"new-line": "\n", r"new-paragraph": "\n\n"}


def parse_word(word):
    word = word.lstrip("\\").split("\\", 1)[0]
    word = mapping.get(word, word)
    return word


keymap = {}
keymap.update(
    {
        "(cd {terminal.subdirs} | cd)": change_dir,
        "list": list_dir,
        "parent": parent,
        "home": ["cd \n", update_ctx],
        "make dir": "mkdir -p ",
        "remove ": "rm ",
        "remove directory": "rm -rf ",
        "scroll down": [Key("shift-pagedown")],
        "scroll up": [Key("shift-pageup")],
        # "run make (durr | dear)": "mkdir ",
        # "run git": "git ",
        # "run git clone": "git clone ",
        # "run git diff": "git diff ",
        # "run git commit": "git commit ",
        # "run git push": "git push ",
        # "run git pull": "git pull ",
        # "run git status": "git status ",
        # "run git add": "git add ",
        # "run (them | vim)": "vim ",
        # "run ellis": "ls\n",
        # "dot pie": ".py",
        # "run make": "make\n",
        # "run jobs": "jobs\n",
        # "const": "const ",
        # "static": "static ",
        "make [<dgndictation>]": ["make ", text],
        "make [<dgndictation>]": ["make ", text],
        # git
        "jet [<dgndictation>]": ["git ", text],
        "jet add [<dgndictation>]": ["git add ", text],
        "jet branch": "git br\n",
        "jet clone [<dgndictation>]": ["git clone ", text],
        "jet checkout master": "git checkout master\n",
        "jet checkout [<dgndictation>]": ["git checkout ", text],
        "jet commit [<dgndictation>]": ["git commit ", text],
        "jet diff": "git diff\n",
        "jet history": "git hist\n",
        "jet merge [<dgndictation>]": ["git merge ", text],
        "jet pull [<dgndictation>]": ["git pull ", text],
        "jet pull (base | rebase) [<dgndictation>]": ["git pull --rebase ", text],
        "jet push [<dgndictation>]": ["git push ", text],
        "jet rebase": "git rebase -i HEAD~",
        "jet stash": "git stash\n",
        "jet status": "git status\n",
        # common
        "gradle": "./gradlew ",
        "gradle deploy": "./gradlew deploy",
        "gradle build": "./gradlew deploy",
        "activate": "act",
        "jump [<dgndictation>]": ["zz ", text, "\n"],
    }
)


ctx.keymap(keymap)
