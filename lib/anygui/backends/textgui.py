# Curses magic implemented on a dumb terminal.
from anygui.backends import *
__all__ = anygui.__all__

import anygui.backends.scr_text as scr_text
import txtsupport
txtsupport._support = scr_text
from txtsupport import *
