import time

from talon.voice import Context, press, Str, Key
from .. import utils

ACTION_POPUP_KEY = "shift-cmd-p"
SELECT_LINE_KEY = "cmd-l"
COMPLETE_KEY = "ctrl-space"
SEARCH_ALL_KEY = "cmd-shift-f"
COMMENT_KEY = "cmd-k cmd-c"
SELECT_MORE_KEY = "cmd-shift-ctrl-right"
SELECT_LESS_KEY = "cmd-shift-ctrl-left"
OPEN_KEY = "cmd+o"
SAVE_KEY = "cmd+s"
NEW_TAB_KEY = "cmd-n"
LAST_TAB_KEY = "cmd-alt-left"
QUICK_OPEN_KEY = "cmd-p"
EXTENSIONS_TAB_KEY = "shift-cmd-x"
VCS_TAB_KEY = "shift-ctrl-g"
DEBUG_TAB_KEY = "shift-cmd-d"
SEARCH_TAB_KEY = "shift-cmd-f"
EXPLORE_TAB_KEY = "shift-cmd-e"
DRAG_DOWN = "alt-down"
DRAG_UP = "alt-up"
FIND_KEY = "cmd-f"
NEXT_TAB_KEY = "cmd-alt-right"
GOTO_LINE_KEY = "ctrl-g"

context = Context("VSCode", bundle="com.microsoft.VSCode")


extendKey = ""


def set_extend(k=""):
    def set_inner(_):
        global extendKey
        extendKey = k

    return set_inner


def eKey(key):
    def _eKey(m):
        global extendKey
        extendKey = key
        Key(key)(m)

    return _eKey


def extend_action(m):
    global extendKey

    # noinspection PyProtectedMember
    count = max(utils.text_to_number([utils.parse_word(w) for w in m._words[1:]]), 1)
    for _ in range(count):
        Key(extendKey)


# Tweaked version of talon_community's util.repeat_function
def repeat_function(drop, key, delay=0):
    def repeater(m):
        # noinspection PyProtectedMember
        line_number = utils.text_to_number(m._words[drop:])

        if line_number is None:
            line_number = 1

        for i in range(0, line_number):
            time.sleep(delay)
            press(key)

    return repeater


def jump_to_line(m):
    # noinspection PyProtectedMember
    line_number = utils.text_to_number(m._words[2:])

    if line_number is None:
        return

    # Zeroth line should go to first line
    if line_number == 0:
        line_number = 1

    press(GOTO_LINE_KEY)
    # time.sleep(0.1)
    Str(str(line_number))(None)
    press("enter")


def jump_tabs(m):
    # noinspection PyProtectedMember
    line_number = utils.text_to_number(m._words[1:])

    if line_number is None:
        return

    for i in range(0, line_number):
        press(NEXT_TAB_KEY)


def jump_to_next_word_instance(m):
    press("escape")
    press(FIND_KEY)
    # noinspection PyProtectedMember
    Str(" ".join([str(s) for s in m.dgndictation[0]._words]))(None)
    press("return")


def select_lines_function(m):
    divider = 0
    # noinspection PyProtectedMember
    for word in m._words:
        if str(word) == "until":
            break
        divider += 1
    # XXX Hardcoded drop of two...
    # noinspection PyProtectedMember
    line_number_from = int(str(utils.text_to_number(m._words[2:divider])))
    # noinspection PyProtectedMember
    line_number_until = int(str(utils.text_to_number(m._words[divider + 1 :])))
    number_of_lines = line_number_until - line_number_from

    press(GOTO_LINE_KEY)
    Str(str(line_number_from))(None)
    press("enter")
    for i in range(0, number_of_lines + 1):
        press("shift-down")


context.keymap(
    {
        # Misc verbs
        "complete": eKey(COMPLETE_KEY),
        # Variants which take text?  Replaced mostly with "call" formatter.
        # "complete <dgndictation> [over]": [eKey("action CodeCompletion"), text],
        # "smart <dgndictation> [over]": [eKey("action SmartTypeCompletion"), text],
        "drag up": eKey(DRAG_UP),
        "drag down": eKey(DRAG_UP),
        "clone (this | line)": eKey("shift-alt-down"),
        # f"clone line {utils.numerals}": [eKey_num("clone {}", drop=2)],
        # f"grab {utils.optional_numerals}": [grab_identifier, set_extend()],
        # "(synchronizing | synchronize)": eKey("action Synchronize"),
        "(action | please)": eKey(ACTION_POPUP_KEY),
        "(action | please) <dgndictation>++ [over]": [
            eKey(ACTION_POPUP_KEY),
            utils.text,
        ],
        f"extend {utils.optional_numerals}": extend_action,

        # XXX Command for Go to Symbol?
        # "to here": to_here,
        # Refactoring
        "refactor": eKey("ctrl-shift-r"),
        "refactor rename": eKey("f2"),
        # "refactor <dgndictation> [over]": [
        #     eKey("action Refactorings.QuickListPopupAction"),
        #     utils.text,
        # ],
        # "extract variable": eKey("action IntroduceVariable"),
        # "extract field": eKey("action IntroduceField"),
        # "extract constant": eKey("action IntroduceConstant"),
        # "extract parameter": eKey("action IntroduceParameter"),
        # "extract interface": eKey("action ExtractInterface"),
        # "extract method": eKey("action ExtractMethod"),
        # Quick Fix / Intentions
        "fix this": eKey("cmd-."),
        "fix this <dgndictation> [over]": [eKey("cmd-."), utils.text],
        "go next (error | air)": eKey("f8"),
        "go last (error | air)": eKey("shift-f8"),
        "fix next (error | air)": [eKey("f8 cmd-.")],
        "fix last (error | air)": [eKey("shift-f8 cmd-.")],
        f"fix line {utils.numerals}": [jump_to_line, eKey("f8 cmd-.")],
        "fix (format | formatting)": eKey("shift-alt-f"),
        # Go: move the caret
        "(go declaration | follow)": eKey("f12"),
        "go implementation": eKey("cmd-f12"),
        "(pop | peek) declaration": eKey("alt-f12"),
        "(pop | peek) implementation": eKey("shift-cmd-f12"),
        "(go | pop | peek) usages": eKey("shift-f12"),
        "go type": [eKey(ACTION_POPUP_KEY), "Go to Type Definition\n", set_extend()],

        "go back": eKey("ctrl--"),
        "go forward": eKey("shift-ctrl--"),
        # "go [to] here": [lambda m: delayed_click(m, from_end=True)],
        # f"go line start {utils.numerals}": eKey_num("goto {} 0", drop=3),
        # f"go line end {utils.numerals}": eKey_num("goto {} 9999", drop=3),
       
        f"go line {utils.numerals}": [jump_to_line, Key("end home")],
        # Select
        # "select here": [
        #     lambda m: delayed_click(m, from_end=True),
        #     eKey("home", "endWithSelection"),
        # ],
        # "select to here": [lambda m: delayed_click(m, from_end=True, mods=["shift"])],
        # "select from here": lambda m: set_to_here(
        #     lambda _: delayed_click(m, from_end=True),
        #     lambda m2: delayed_click(m2, from_end=True, mods=["shift"]),
        # ),
        "(correct | select phrase)": utils.select_last_insert,  # Nothing fancy for now.
        # "select last <dgndictation> [over]": [eKey_find("prev")],
        # "select next <dgndictation> [over]": [eKey_find("next")],
        # "select last bounded {jetbrains.alphabet}+": [eKey_bounded("prev")],
        # "select next bounded {jetbrains.alphabet}+": [eKey_bounded("next")],
        "select less": eKey(SELECT_LESS_KEY),
        "select more": eKey(SELECT_MORE_KEY),
        "select this": eKey(SELECT_MORE_KEY),
        "multi-select up": eKey("alt-cmd-up"),
        "multi-select down": eKey("alt-cmd-down"),
        # "multi-select fewer": eKey("alt-cmd-up"),
        # "multi-select more": eKey("alt-cmd-up"),
        "multi-select all": eKey("alt-cmd-l"),
        "select line": eKey(SELECT_LINE_KEY),
        f"select line {utils.numerals}": [jump_to_line, eKey(SELECT_LINE_KEY)],
        # f"select lines {utils.numerals} until {utils.numerals}": eKey_range(
        #     "range {} {}", drop=2
        # ),
        # f"select until line {utils.numerals}": eKey_num("extend {}", drop=3),
        # Search
        "(jump | search everywhere)": eKey(QUICK_OPEN_KEY),
        "(jump | search everywhere) <dgndictation> [over]": [
            eKey(QUICK_OPEN_KEY),
            utils.text,
            set_extend(),
        ],
        "recent": [eKey(QUICK_OPEN_KEY), set_extend()],
        "recent <dgndictation> [over]": [
            eKey(QUICK_OPEN_KEY),
            utils.text,
            set_extend(),
        ],
        "search [this]": eKey(FIND_KEY),
        "search for <dgndictation> [over]": [
            eKey(FIND_KEY),
            utils.text,
            set_extend("cmd-g"),
        ],
        # "go next search": eKey("cmd-g"),
        # "go last search": eKey("shift-cmd-g"),
        "go next result": eKey("cmd-g"),
        "go last result": eKey("shift-cmd-g"),
        "search in path": eKey(SEARCH_ALL_KEY),
        "search in path <dgndictation> [over]": [eKey(SEARCH_ALL_KEY), utils.text],
        # Lines / Selections
        "clear phrase": [utils.select_last_insert, eKey("delete")],
        "clear line": [eKey("end shift-home delete")],
        f"clear line {utils.numerals}": [
            jump_to_line,
            eKey("end"),
            eKey("shift-home delete"),
        ],
        "clear this": [eKey(SELECT_MORE_KEY), eKey("delete")],
        # "clear last <dgndictation> [over]": [
        #     eKey_find("prev"),
        #     eKey("delete"),
        #     set_extend(extendKey + " delete"),
        # ],
        # "clear next <dgndictation> [over]": [
        #     eKey_find("next"),
        #     eKey("delete"),
        #     set_extend(extendKey + " delete"),
        # ],
        # "clear last bounded {jetbrains.alphabet}+": [
        #     eKey_bounded("prev"),
        #     eKey("delete"),
        #     set_extend(extendKey + " delete"),
        # ],
        # "clear next bounded {jetbrains.alphabet}+": [
        #     eKey_bounded("next"),
        #     eKey("delete"),
        #     set_extend(extendKey + " delete"),
        # ],
        "clear line end": eKey("shift-end delete"),
        "clear line start": eKey("shift-home delete"),
        f"clear lines {utils.numerals} until {utils.numerals}": [
            select_lines_function,
            eKey("delete"),
        ],
        # f"clear until line {utils.numerals}": [
        #     eKey_num("extend {}", drop=3),
        #     eKey("delete"),
        # ],
        # Commenting
        "comment phrase": [utils.select_last_insert, eKey("cmd-k cmd-c")],
        "comment line": eKey("cmd-k cmd-c"),
        # "comment here": [
        #     lambda m: delayed_click(m, from_end=True),
        #     eKey("home", "cmd-k cmd-c"),
        # ],
        # "comment to here": [
        #     lambda m: delayed_click(m, from_end=True, mods=["shift"]),
        #     eKey("cmd-k cmd-c"),
        # ],
        # "comment from here": lambda m: set_to_here(
        #     lambda _: delayed_click(m, from_end=True),
        #     lambda m2: delayed_click(m2, from_end=True, mods=["shift"]),
        #     lambda _: time.sleep(0.2),
        #     eKey("cmd-k cmd-c"),
        # ),
        f"comment line {utils.numerals}": [
            jump_to_line,
            eKey("end"),
            eKey("cmd-k cmd-c"),
        ],
        # "comment last <dgndictation> [over]": [
        #     eKey_find("prev"),
        #     eKey("home"),
        #     eKey("cmd-k cmd-c"),
        # ],
        # "comment next <dgndictation> [over]": [
        #     eKey_find("next"),
        #     eKey("home"),
        #     eKey("cmd-k cmd-c"),
        # ],
        # "comment last bounded {jetbrains.alphabet}+": [
        #     eKey_bounded("prev"),
        #     eKey("home"),
        #     eKey("cmd-k cmd-c"),
        # ],
        # "comment next bounded {jetbrains.alphabet}+": [
        #     eKey_bounded("next"),
        #     eKey("home"),
        #     eKey("cmd-k cmd-c"),
        # ],
        "comment line end": [eKey("endWithSelection"), eKey("cmd-k cmd-c")],
        f"comment lines {utils.numerals} until {utils.numerals}": [
            select_lines_function,
            eKey("cmd-k cmd-c"),
        ],
        # f"comment until line {utils.numerals}": [
        #     eKey_num("extend {}", drop=3),
        #     eKey("cmd-k cmd-c"),
        # ],
        # Selecting text
        "select line"
        + utils.optional_numerals
        + "until"
        + utils.optional_numerals: select_lines_function,
        # Splits
        "split vertically": eKey("cmd-\\"),
        "split horizontally": eKey("cmd-k cmd-\\"),
        "split flip": eKey("cmd-alt-0"),
        "split window": eKey("cmd-k o"),
        "go next split": eKey("cmd-k cmd-right"),  # Assumes vertical split!
        "go last split": eKey("cmd-k cmd-left"),
        "copy path": eKey("alt-cmd-c"),
        # Breakpoints / debugging
        "toggle [line] breakpoint": eKey("f9"),
        "step over": eKey("f10"),
        "step into": eKey("f11"),
        # Dash Searching
        "go [smart] dash": eKey("ctrl-h"),
        "go all dash": eKey("ctrl-alt-h"),
        # Camel bindings need an extension!
        # "go camel left": eKey("action EditorPreviousWordInDifferentHumpsMode"),
        # "go camel right": eKey("action EditorNextWordInDifferentHumpsMode"),
        # "select camel left": eKey(
        #     "action EditorPreviousWordInDifferentHumpsModeWithSelection"
        # ),
        # "select camel right": eKey(
        #     "action EditorNextWordInDifferentHumpsModeWithSelection"
        # ),
        # "clear camel left": eKey(
        #     "action EditorPreviousWordInDifferentHumpsModeWithSelection",
        #     "action EditorBackSpace",
        # ),
        # "clear camel right": eKey(
        #     "action EditorNextWordInDifferentHumpsModeWithSelection",
        #     "action EditorBackSpace",
        # ),
        # "copy camel left": eKey(
        #     "action EditorPreviousWordInDifferentHumpsModeWithSelection",
        #     "action EditorCopy",
        # ),
        # "copy camel right": eKey(
        #     "action EditorNextWordInDifferentHumpsModeWithSelection",
        #     "action EditorCopy",
        # ),
        # "cut camel left": eKey(
        #     "action EditorPreviousWordInDifferentHumpsModeWithSelection",
        #     "action EditorCut",
        # ),
        # "cut camel right": eKey(
        #     "action EditorNextWordInDifferentHumpsModeWithSelection", "action EditorCut"
        # ),
        "(template | snippet)": [
            eKey(ACTION_POPUP_KEY),
            "Insert Snippet\n",
            set_extend(),
        ],
        "(template | snippet) <dgndictation> [over]": [
            eKey(ACTION_POPUP_KEY),
            "Insert Snippet\n",
            utils.delay(0.3),
            utils.text,
        ],
        "create (template | snippet)": [
            eKey(ACTION_POPUP_KEY),
            "Configure User Snippets\n",
            set_extend(),
        ],
        "toggle explore": eKey(EXPLORE_TAB_KEY),
        "toggle search": eKey(SEARCH_TAB_KEY),
        "toggle debug": eKey(DEBUG_TAB_KEY),
        "toggle jet": eKey(VCS_TAB_KEY),
        "toggle extensions": eKey(EXTENSIONS_TAB_KEY),
        "toggle (tools | sidebar)": eKey("cmd-b"),
        # XXX These need to go to generic editor interface
        # tabbing
        "next tab": eKey(NEXT_TAB_KEY),
        "last tab": eKey(LAST_TAB_KEY),
        "new tab": eKey(NEW_TAB_KEY),
        # "jump" + utils.optional_numerals: jump_tabs,
        # Menu
        "save file": eKey(SAVE_KEY),
        "open file": eKey(OPEN_KEY),
    }
)
