# Curses magic implemented on a dumb terminal.
from anygui.backends import *
__all__ = anygui.__all__

import anygui.backends.txtutils.scr_text as scr_text
import anygui.backends.txtutils.txtgui as txtgui
txtgui._support = scr_text
from anygui.backends.txtutils.txtgui import *
