# Curses magic...
from anygui.backends import *
__all__ = anygui.__all__

from anygui.Exceptions import Error

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

import anygui.backends.txtutils.scr_curses as scr_curses
scr_curses.scr_init()
import anygui.backends.txtutils.txtgui as txtgui
txtgui._scr = scr_curses
x,y = scr_curses._xsize,scr_curses._ysize
scr_curses.dbg("x,y=",x,y)
txtgui._set_scale(x,y)
from anygui.backends.txtutils.txtgui import *
