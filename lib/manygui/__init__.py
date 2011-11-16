_backends = 'msw gtk java wx tk beos qt curses text'
#_backends = 'java msw wx qt tk'

# 20020208:mlh -- starting to experiment with new architecture
__all__ = """

  Application
  Frame
  GroupBox
  Button
  CheckBox
  Options
  Events
  Window
  Label
  TextField
  TextArea
  ListBox
  ComboBox
  RadioButton
  RadioGroup
  BooleanModel
  ListModel
  TextModel
  any
  application
  backend
  link
  send
  sender
  setup
  unlink
  unlinkHandler
  unlinkMethods
  unlinkSource

""".split()

# When the Borg pattern is in use, this is no longer needed:
def application():
    'Returns the global application object'
    #global _application
    if not _application:
        #_application = backendModule().Application()
        raise RuntimeError('no application exists')
    return _application

def backend():
    'Returns the name of the current backend'
    if not _backend_name:
        raise RuntimeError('no backend exists')
    return _backend_name

def backendModule():
    'Returns the current backend module'
    if not _backend:
        raise RuntimeError('no backend exists')
    return _backend

def setup(self, **kwds):
    'Used to configure Manygui'
    raise NotImplementedError


########## Begin Imports ##################################################

import os, sys
from manygui.Attribs          import Attrib
from manygui.Utils            import Options
#from manygui.Applications     import AbstractApplication
from manygui.Windows          import Window
from manygui.Buttons          import Button
#from manygui.Canvases         import Canvas
#from manygui                  import Colors
from manygui.Labels           import Label
from manygui.CheckBoxes       import CheckBox
from manygui.RadioButtons     import RadioButton
from manygui.RadioGroups      import RadioGroup
from manygui.TextFields       import TextField
from manygui.TextAreas        import TextArea
from manygui.ListBoxes        import ListBox
from manygui.ComboBoxes       import ComboBox
from manygui.Models           import BooleanModel, ListModel, TextModel
from manygui.Events           import *
from manygui.Frames           import Frame, GroupBox
from manygui.LayoutManagers   import LayoutManager, Placer
from manygui.Menus            import MenuBar, Menu, MenuCommand, MenuCheck, MenuSeparator

########### End Imports ###################################################

"""
# Original export list:
__all__ = ['application', 'Application',
           'Window', 'Button', 'CheckBox', 'Label',
           'RadioButton', 'RadioGroup', 'ListBox', 'TextField', 'TextArea',
           'BooleanModel', 'ListModel', 'TextModel', 'Options',
           'LayoutManager', 'Placer',
           'send', 'sender', 'link', 'unlink', 'any', 'unlinkSource', 'unlinkHandler',
           'unlinkMethods', 'Frame', 'Placer', 'backend'
           ] # FIXME: Add stuff from Colors and Fonts
"""

# Try to get the environment variables ANYGUI_WISHLIST (overrides
# manygui.wishlist), and ANYGUI_DEBUG (to print out stacktraces when
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

_application  = None
_backend      = None
_backend_name = None

def _dotted_import(name):
    # version of __import__ which handles dotted names
    # copied from python docs for __import__
    import string
    mod = __import__(name, globals(), locals(), [])
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def _backend_passthrough():
    global _backends, _backend, _backend_name
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
            mod = _dotted_import('manygui.backends.%sgui' % name,)
            for key in mod.__all__:
                globals()[key] = mod.__dict__[key]
        except (ImportError, AttributeError, KeyError):
            if DEBUG and not (DEBUG in _backends and not DEBUG==name):
                import traceback
                traceback.print_exc()
            continue
        else:
            _backend_name = name
            _backend      = mod
            return
    raise RuntimeError("no usable backend found")

# Pass the backend namespace through:
_backend_passthrough()
