# Curses magic...
from anygui.backends import *
__all__ = anygui.__all__

import scr_curses
import txtsupport
txtsupport._support = scr_curses
from txtsupport import *
