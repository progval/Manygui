_backends = 'msw gtk x java wx tk beos'

# Try to get the environment variables ANYGUI_WISHLIST (used
# before anygui.wishlist), and ANYGUI_DEBUG (to print out
# stacktraces when importing backends):

import os, sys

__all__ = ['application', 'Application',
           'Window', 'Button', 'CheckBox', 'Label',
           'RadioButton', 'RadioGroup', 'ListBox', 'TextField', 'TextArea',
           'BooleanModel', 'ListModel', 'TextModel', 'Options',
           'send', 'connect', 'disconnect'] # Add Frame when all backends support it

if hasattr(sys, 'registry'):
    # Jython:
    wishlist = sys.registry.getProperty('ANYGUI_WISHLIST', _backends).split()
    DEBUG = sys.registry.getProperty('ANYGUI_DEBUG', '0')
else:
    # CPython:
    wishlist = os.environ.get('ANYGUI_WISHLIST', _backends).split()
    DEBUG = os.environ.get('ANYGUI_DEBUG', '0')

# Non-empty string may be zero (i.e. false):
if DEBUG:
    try:
        DEBUG = int(DEBUG)
    except ValueError:
        pass

_application = None

def _dotted_import(name):
    # version of __import__ which handles dotted names
    # copied from python docs for __import__
    import string
    mod = __import__(name, globals(), locals(), [])
    components = string.split(name, '.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def _backend_passthrough():
    global _backends
    _backends = _backends.split()
    _backends = [b for b in _backends if not b in wishlist]
    _backends = wishlist + _backends
    for name in _backends:
        try:
            mod = _dotted_import('anygui.backends.%sgui' % name,)
            for key in __all__:
                globals()[key] = mod.__dict__[key]
        except (ImportError, AttributeError):
            if DEBUG:
                import traceback
                traceback.print_exc()
            continue
        else:
            return
    raise RuntimeError, "no usable backend found"

def application():
    """Return the global application object"""
    global _application
    if not _application:
        #_application = factory()._map['Application']()
        raise RuntimeError, 'no application exists'
    return _application

# Pass the backend namespace through:
_backend_passthrough()
