import os
import sys
import types

from inspect import signature

talon_modules = [m for m in sys.modules.keys() if m.startswith("talon.")]
# talon_modules = ["talon.clip"]
talon_plugin_modules = [m for m in sys.modules.keys() if m.startswith("talon_plugins.")]


def dump_stubs(mod_name, mod):
    output = ["from types import *", f"import {mod_name}"]
    for id in dir(mod):
        # print(mod, id)
        thing = getattr(mod, id)
        if callable(thing):
            try:
                output.append(f"def {id}{str(signature(thing))}: ...")
            except Exception as e:
                print(e)
                output.append(f"def {id}(*args, **kwargs) -> Any: ...")
        # elif isinstance(thing, object):
        #     output.append(f"class {thing.__name__}{str(signature(thing))}:")

    return "\n".join(output)


STUBS_DIR = os.path.expanduser("~/.talon/stubs")
try:
    os.mkdirs(STUBS_DIR)
except:
    pass

for m in talon_modules:
    # print(m)
    name = m.split(".")[-1] + ".pyi"
    with open(os.path.join(STUBS_DIR, "talon", name), "w") as fh:
        stubs = dump_stubs(m, sys.modules[m])
        # print(stubs)
        fh.write(stubs)
