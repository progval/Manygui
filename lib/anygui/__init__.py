import os

backends = 'x java wx tk beos'
wishlist = os.getenv('ANYGUI_WISHLIST', 'x java wx tk beos').split()

# set to true to see tracebacks when searching for factories
DEBUG=0

_application = None
_factory = None

def _dotted_import(name):
    # version of __import__ which handles dotted names
    # copied from python docs for __import__
    import string
    mod = __import__(name)
    components = string.split(name, '.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def _get_factory():
    global backends
    backends = backends.split()
    backends = [b for b in backends if not b in wishlist]
    backends = wishlist + backends
    for name in backends:
        try:
            module = _dotted_import('anygui.backends.%sgui' % name, )
        except ImportError:
            if DEBUG:
                import traceback
                traceback.print_exc()
            continue
        try:
            factory = getattr(module, 'factory')
        except AttributeError:
            if DEBUG:
                import traceback
                traceback.print_exc()
            continue
        else:
            return factory()
    raise RuntimeError, "no usable backend found"


################################################################
#
# anygui itself
#

class ImpIsDelegate:
    def __init__(self, *args, **kw):
        self.__dict__['_imp'] = factory()._map[self._class_](*args, **kw)
    
    def __getattr__(self, name):
        return getattr(self._imp, name)

    def __setattr__(self, name, value):
        return setattr(self._imp, name, value)

class Window(ImpIsDelegate):
    _class_ = 'Window'

class Button(ImpIsDelegate):
    _class_ = 'Button'

class Label(ImpIsDelegate):
    _class_ = 'Label'

class CheckBox(ImpIsDelegate):
    _class_ = 'CheckBox'

class RadioButton(ImpIsDelegate):
    _class_ = 'RadioButton'

class RadioGroup(ImpIsDelegate):
    _class_ = 'RadioGroup'

class ListBox(ImpIsDelegate):
    _class_ = 'ListBox'

class TextField(ImpIsDelegate):
    _class_ = 'TextField'

class TextArea(ImpIsDelegate):
    _class_ = 'TextArea'

class Application(ImpIsDelegate):
    _class_ = 'Application'

def application():
    """Return the global application object"""
    global _application
    if not _application:
        _application = factory()._map['Application']()
    return _application

def factory():
    """Return the global factory object"""
    global _factory
    if not _factory:
        _factory = _get_factory()
    return _factory

__all__ = ['application', 'Application', 'factory', 'wishlist', \
           'Window', 'Button', 'CheckBox', 'Label', \
           'RadioButton', 'RadioGroup', 'ListBox', 'TextField', 'TextArea']
