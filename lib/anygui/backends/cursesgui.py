# Curses magic...
from anygui.backends import *
#__all__ = anygui.__all__

__all__ = '''

  Application
  ButtonWrapper
  WindowWrapper
  LabelWrapper
  TextFieldWrapper
  TextAreaWrapper
  ListBoxWrapper
  RadioButtonWrapper
  CheckBoxWrapper

'''.split()

Application=1
ButtonWrapper=1
WindowWrapper=1
LabelWrapper=1
TextFieldWrapper=1
TextAreaWrapper=1
ListBoxWrapper=1
RadioButtonWrapper=1
CheckBoxWrapper=1

from anygui.Exceptions import Error
from anygui.Utils import setLogFile
setLogFile('curses.txt')

import sys
import os
if hasattr(sys,'ps1'):
    try:
        os.environ['ANYGUI_FORCE_CURSES']
    except KeyError:
        raise ImportError,"This appears to be an interactive session; curses disabled."

import atexit

def _cleanup():
    try:
        scr_curses.scr_quit()
    except:
        pass

atexit.register(_cleanup)

import anygui.backends.txtutils.txtgui as txtgui
txtgui.setScreenPackage("curses")
from anygui.backends.txtutils.txtgui import *
