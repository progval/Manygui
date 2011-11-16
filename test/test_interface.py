# TODO: Use unittest
import sys
sys.exit('test_interface is not currently pertinent')

from manygui.Utils import log

import manygui

backends = []

log("Checking backend __all__ attributes:")

for b in manygui._backends:
    try:
        mod = manygui._dotted_import('manygui.backends.%sgui' % b)
        backends.append((mod, b))
    except:
        log("[%sgui ignored]" % b)

for mod, name in backends:
    if mod.__all__ != manygui.__all__:
        log('Export error for %sgui' % name )
        log('manygui exports:')
        for exp in manygui.__all__:
            log('\t -%s' % exp)
        log('%sgui exports:' % name)
        for exp in mod.__all__:
            log('\t- %s' % exp)
    raise AssertionError('%sgui should export the same API as manygui!' % name)
    log('%sgui OK' % name)
