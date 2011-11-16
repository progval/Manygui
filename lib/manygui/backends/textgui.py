# Curses magic implemented on a dumb terminal.

from manygui.backends import *
from manygui.Utils import log, setLogFile
setLogFile('textgui.txt')

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


################################################################

# Cut for 0.2.
#from manygui.backends import *
#__all__ = manygui.__all__

import manygui.backends.txtutils.txtgui as txtgui
txtgui.setScreenPackage('text')
from manygui.backends.txtutils.txtgui import *
