# Curses magic implemented on a dumb terminal.
from anygui.backends import *
__all__ = anygui.__all__

import anygui.backends.txtutils.scr_text as scr_text
import anygui.backends.txtutils.txtgui as txtgui
txtgui._scr = scr_text
x,y = scr_text._xsize,scr_text._ysize
txtgui._set_scale(x,y)
for key in __all__:
    globals()[key] = txtgui.__dict__[key]
globals()['Canvas'] = txtgui.__dict__['Canvas']
