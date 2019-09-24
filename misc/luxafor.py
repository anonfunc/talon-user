import subprocess

from talon import keychain, cron, applescript
from talon_plugins.speech import talon as tcg

import requests

# https://luxafor.com/webhook-api/
# at the repl, keychain.add("luxafor", "webhookid", "ID")
try:
    WEBHOOK_ID = keychain.find("luxafor", "webhookid")
except:
    WEBHOOK_ID = ""

USE_WEBHOOK = False

# https://github.com/anonfunc/light-flag.git
SHELL_SOLID = "~/bin/light-flag -solid {color} -mini {mini}"
SHELL_BLINK = "~/bin/light-flag -blink {blink} -side back"
COLOR = None
MINI = None


def solid_color(color, mini=None):
    global COLOR, MINI
    if mini is None:
        mini = color
    if COLOR == color and MINI == mini:
        return
    if USE_WEBHOOK:
        requests.post(
            "https://api.luxafor.com/webhook/v1/actions/solid_color",
            json={"userId": WEBHOOK_ID, "actionFields": {"color": color}},
            headers={"Content-Type": "application/json"},
        ).raise_for_status()
    else:
        cmd = SHELL_SOLID.format(color=color, mini=mini)
        p = subprocess.Popen(cmd, shell=True)

    COLOR = color
    MINI = mini


def blink_color(color):
    if USE_WEBHOOK:
        requests.post(
            "https://api.luxafor.com/webhook/v1/actions/blink",
            json={"userId": WEBHOOK_ID, "actionFields": {"color": color}},
            headers={"Content-Type": "application/json"},
        ).raise_for_status()
    else:
        cmd = SHELL_BLINK.format(color=COLOR, blink=color)
        subprocess.check_call(cmd, shell=True)


def set_color_for_main():
    base_color = "red" if tcg.enabled else "green"
    if running_screensaver():
        solid_color("blue", mini=base_color)
    else:
        solid_color(base_color)


def running_screensaver():
    return (
        applescript.run(
            """
            tell application "System Events"
            get running of screen saver preferences
            end tell
            """
        )
        == "true"
    )


cron.interval("2s", set_color_for_main)
