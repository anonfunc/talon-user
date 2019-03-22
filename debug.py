from talon.engine import engine
import json


def listener(topic, m):
    cmd = m["cmd"]
    #  Just comment these out if you want the hairy objects.
    if topic == "cmd" and cmd["cmd"] == "g.load" and m["success"] == True:
        print("[grammar reloaded]")
    elif topic == "cmd" and cmd["cmd"] == "g.listset":
        print(f'[list {m["cmd"]["list"]} updated: {m["cmd"]["items"][0:6]}...]')
    elif topic == "cmd" and cmd["cmd"] == "g.update":
        print("[user scripts updated]")
    elif topic == "cmd" and cmd["cmd"] == "g.unload":
        print("[user scripts unloaded]")
    elif topic == "cmd" and cmd["cmd"] in {"w.add", "w.remove"}:
        print("[dragon vocab updated]")
    elif topic == "phrase" and cmd == "p.end":
        if "parsed" in m:
            print(f'[phase: {m["parsed"]}]')
    else:
        print(topic, m)


# Uncomment to enable.
#engine.register('', listener)
def unload():
    engine.unregister("", listener)


# unload()
