# Curses magic...
from anygui.backends import *
__all__ = anygui.__all__

import scr_curses
scr_curses.scr_init()
import txtsupport
txtsupport._support = scr_curses
x,y = scr_curses._xsize,scr_curses._ysize
txtsupport._set_scale(x,y)
from txtsupport import *
