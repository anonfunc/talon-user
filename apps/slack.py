import random
import subprocess
import time

from talon import ui
from talon.voice import Context, Key, Str

from ..utils import text, join_words, parse_words, insert, delay

alpha_to_emoji = {
    " ": [":white_small_square:"],
    "'": [":droplet:"],
    "a": [":amazon:", ":braves:", ":laa:", ":arch:", ":a:"],
    "b": [":bonusly:", ":boston:", ":bucknell:", ":b:", ":bitcoin:", ":bootstrap:"],
    "c": [":canvas:", ":costco:", ":copyright:"],
    "d": [":duo:", ":leftwards_arrow_with_hook:"],
    "e": [":espresa:", ":ielogo:", ":e-mail:"],
    "f": [":falcons:", ":payrespects:", ":flutter:"],
    "g": [":googleicon:", ":georgia_bulldogs:", ":grafana:", ":google:"],
    "h": [":hotel:", ":sa:", ":pisces:"],
    "i": [":illini:", ":information_source:"],
    "j": [":arrow_heading_up:"],
    "k": [":kotlin:"],
    "l": [":l:", ":muscle:", ":lambda:"],
    "m": [":michiganblock:", ":scorpius:", ":mcdonalds:", ":mini:"],
    "n": [":nagios:", ":nespresso:", ":nu:", ":pr:"],
    "o": [":okta:", ":goducks:", ":outlook:", ":portal1:", ":o:", ":o2:"],
    "p": [":paypal:", ":philly:", ":ptown:", ":badparking:"],
    "q": [":q:", ":clock430:"],
    "r": [":revolut:", ":registered:", ":rust:"],
    "s": [":skype:", ":trogdor-stomp:", ":heavy_dollar_sign:", ":sooperheroes:"],
    "t": [":text:", ":tesla:", ":text:", ":terraform:"],
    "u": [":jedi:", ":ophiuchus:", ":utah_state_aggies:"],
    "v": [":venmo:", ":aries:"],
    "w": [
        ":wday:",
        ":googlewallet:",
        ":flythew:",
        ":wow:",
        ":wutang:",
        ":wu-tang:",
        ":wumbo:",
    ],
    "x": [":x:", ":heavy_multiplication_x:"],
    "y": [":valor:", ":yeet:", ":funnel:", ":byu:"],
    "z": [":zap:", ":z:"],
}


def emoji_formatter(m):
    string = join_words(parse_words(m))
    insert(
        "".join([random.choice(alpha_to_emoji.get(c.lower(), [""])) for c in string])
    )


def emoji_reaction_formatter(m):
    string = join_words(parse_words(m))
    translated = [random.choice(alpha_to_emoji.get(c.lower(), [""])) for c in string]
    for t in translated:
        Str(f"+{t}\n")(m)
        time.sleep(0.7)


ctx = Context("slack", bundle="com.tinyspeck.slackmacgap")
ctx.keymap(
    {
        "focus next": [Key("f6")],
        "jump [<dgndictation>]": [Key("cmd-k"), text],
        "go (dm's | direct messages | messages)": Key("cmd-shift-k"),
        "go (and read | unread)": Key("cmd-shift-a"),
        "go (threads | thread)": Key("cmd-shift-t"),
        "go activity": Key("cmd-shift-m"),
        "go channel info": Key("cmd-shift-i"),
        "go status": Key("cmd-shift-y"),
        "go (star | stars | starred)": Key("cmd-shift-s"),
        "react [<dgndictation>]": ["+:", text],
        "emote [<dgndictation>]": [":", text],
        "toggle sidebar": Key("cmd-."),
        "go last unread": Key("alt-shift-up"),
        "go next unread": Key("alt-shift-down"),
        "annoying <dgndictation> [over]": emoji_formatter,
        "annoying reaction <dgndictation> [over]": emoji_reaction_formatter,
    }
)


def toggle_slack_dnd(amount=""):
    def _toggle_slack_dnd(m):
        window = ui.active_window()
        # Open a slack window to yourself in a browser, scrape these values out of it.
        subprocess.call(["open", "slack://channel?id=D865P648K&team=T03R7LB3M"])
        time.sleep(1)
        Str(f"/dnd {amount}\n")(None)
        Key("cmd-[")(None)
        window.focus()

    return _toggle_slack_dnd


gctx = Context("slackglobal")
gctx.keymap(
    {
        "slack do not disturb": toggle_slack_dnd("until tomorrow morning"),
        "slack do not disturb off": toggle_slack_dnd("off"),
        "slack do not disturb thirty": toggle_slack_dnd("30m"),
    }
)
