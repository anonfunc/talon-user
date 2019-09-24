import random

from talon.voice import Context, Key

from ..utils import text, join_words, parse_words, insert

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
    "w": [":wday:", ":googlewallet:", ":flythew:", ":wow:", ":wutang:", ":wu-tang:", ":wumbo:"],
    "x": [":x:", ":heavy_multiplication_x:"],
    "y": [":valor:", ":yeet:", ":funnel:", ":byu:"],
    "z": [":zap:", ":z:"],
}


def emoji_formatter(m):
    string = join_words(parse_words(m))
    insert("".join([random.choice(alpha_to_emoji.get(c.lower(), [""])) for c in string]))


ctx = Context("slack", bundle="com.tinyspeck.slackmacgap")
ctx.keymap(
    {
        "jump [<dgndictation>]": [Key("cmd-k"), text],
        "go (dm's | direct messages | messages)": Key("cmd-shift-k"),
        "go (and read | unread)": Key("cmd-shift-a"),
        "go (threads | thread)": Key("cmd-shift-t"),
        "react [<dgndictation>]": [Key("cmd-shift-\\"), text],
        "emote [<dgndictation>]": [":", text],
        "toggle zoom": Key("cmd-."),
        "go last unread": Key("alt-shift-up"),
        "go next unread": Key("alt-shift-down"),
        "annoying <dgndictation> [over]": emoji_formatter,
    }
)
