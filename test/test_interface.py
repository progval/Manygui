# TODO: Use unittest
import sys
sys.exit('test_interface is not currently pertinent')

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
    if mod.__all__ != anygui.__all__:
        log('Export error for %sgui' % name )
        log('anygui exports:')
        for exp in anygui.__all__:
            log('\t -%s' % exp)
        log('%sgui exports:' % name)
        for exp in mod.__all__:
            log('\t- %s' % exp)
    raise AssertionError('%sgui should export the same API as anygui!' % name)
    log('%sgui OK' % name)
