#_backends = 'msw gtk java wx tk beos qt curses text'
# beos and gtk removed for first beta:
_backends = 'msw java wx tk qt beos curses text'

import os, sys

__all__ = ['application', 'Application',
           'Window', 'Button', 'CheckBox', 'Label',
           'RadioButton', 'RadioGroup', 'ListBox', 'TextField', 'TextArea',
           'BooleanModel', 'ListModel', 'TextModel', 'Options',
           'LayoutManager', 'Placer',
           'send', 'link', 'unlink', 'any', 'unlinkSource', 'unlinkHandler',
           'unlinkMethods', 'Frame', 'Placer', 'backend'
           ] # FIXME: Add stuff from Colors and Fonts

# Try to get the environment variables ANYGUI_WISHLIST (overrides
# anygui.wishlist), and ANYGUI_DEBUG (to print out stacktraces when
# importing backends):

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
_backend     = None

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
    global _backends, _backend
    _backends = _backends.split()
    _backends = [b for b in _backends if not b in wishlist]
    if wishlist:
        try:
            idx = wishlist.index('*')
            wishlist[idx:idx+1] = _backends
        except ValueError: pass
        _backends = wishlist
    for name in _backends:
        try:
            mod = _dotted_import('anygui.backends.%sgui' % name,)
            for key in __all__:
                globals()[key] = mod.__dict__[key]
        except (ImportError, AttributeError, KeyError):
            if DEBUG and not (DEBUG in _backends and not DEBUG==name):
                import traceback
                traceback.print_exc()
            continue
        else:
            _backend = name
            return
    raise RuntimeError, "no usable backend found"

def application():
    'Return the global application object'
    #global _application
    if not _application:
        #_application = factory()._map['Application']()
        raise RuntimeError, 'no application exists'
    return _application

def backend():
    'Return the name of the current backend'
    if not _backend:
        raise RuntimeError, 'no backend exists'
    return _backend

# Pass the backend namespace through:
_backend_passthrough()
