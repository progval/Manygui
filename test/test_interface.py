# TODO: Use unittest
from anygui.Utils import log

import anygui

backends = []

log("Checking backend __all__ attributes:")

for b in anygui._backends:
    try:
        mod = anygui._dotted_import('anygui.backends.%sgui' % b)
        backends.append((mod, b))
    except:
        log("[%sgui ignored]" % b)

for mod, name in backends:
    assert mod.__all__ == anygui.__all__, ('%sgui should export the same API as anygui' % name)
    log("%sgui OK" % name)
