import os
import sys
import time
from inspect import signature
from textwrap import dedent

INCLUDED_PRIVATE_MEMBERS = ["__init__", "__call__", "_words"]

talon_modules = [
    m
    for m in sys.modules.keys()
    if m.startswith("talon.") or m.startswith("talon_plugins.")
]
# talon_modules = ["talon.clip"]
# talon_plugin_modules = [m for m in sys.modules.keys() if m.startswith("talon_plugins.")]
# print(talon_plugin_modules)


def dump_stubs(mod, indent=""):
    output = []
    for identifier in dir(mod):
        # print(mod, id)
        if identifier.startswith("_") and identifier not in INCLUDED_PRIVATE_MEMBERS:
            continue
        # noinspection PyBroadException
        try:
            thing = getattr(mod, identifier)
        except:
            continue
        if callable(thing):
            output.append(stub_callable(identifier, thing, indent))
        else:
            type_name = type(thing).__name__
            if type_name == "module" or identifier.startswith("_"):
                continue
            # noinspection PyBroadException
            try:
                output.append(f"{identifier}: {type_name} = ...")
            except:
                # print(e)
                output.append(f"{identifier} = ...")
    if len(output) == 0:
        return "..."
    return f"\n{indent}" + f"\n{indent}".join(
        [
            o.replace("<no value>", '"unknown value"')
            .replace("NoneType", "Any")
            .replace("<class ", "")
            .replace("'>", "'")
            for o in output
        ]
    )


def stub_callable(identifier, thing, indent):
    if callable(thing):
        if not isinstance(thing, type):
            # noinspection PyBroadException
            try:
                return f"def {identifier}{str(signature(thing))}: ..."
            except:
                return f"def {identifier}(*args, **kwargs) -> Any: ..."
        else:
            return f"class {identifier}: " + dump_stubs(thing, indent=indent + "   ")


STUBS_DIR = os.path.expanduser("~/.talon/user")


def dump_all_stubs():
    os.makedirs(STUBS_DIR, exist_ok=True)
    super_import = (
        "\n".join(
            [
                f"from {t} import *"
                for t in talon_modules + ["talon.stubbed"]
                if t != "talon.voice"
            ]
        )
        + "\n"
    )
    for m in talon_modules:
        name = ".".join(m.split("."))
        if "." in name:
            path_join = os.path.join(STUBS_DIR, "/".join(name.split(".")[:-1]))
            os.makedirs(path_join, exist_ok=True)
        output_path = os.path.join(STUBS_DIR, name.replace(".", "/"))
        with open(output_path + ".pyi", "w") as fh:
            stubs = dump_stubs(sys.modules[m])
            fh.write("from typing import *\n")
            # fh.write(super_import)
            fh.write(stubs)
    with open(os.path.join(STUBS_DIR, "talon", "stubbed.pyi"), "w") as fh:
        stub = dedent("""\
        from typing import *
        CompiledLib: Any = ...
        CompiledFFI: Any = ...
        class _cffi_backend:
            CData: Any = ...
        getset_descriptor: Any = ...
        """)
        fh.write(
            stub
        )
    with open(os.path.join(STUBS_DIR, "talon", "__init__.pyi"), "w") as fh:
        fh.write(
            dedent(
                """\
        from typing import *
        """
            )
        )
    print("Done stubbing.")


# if time.time() - os.path.getmtime(os.path.join(STUBS_DIR, "talon", "__init__.pyi")) > 3600:
#     dump_all_stubs()
dump_all_stubs()
