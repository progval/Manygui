from anygui import backend
from anygui.Utils import log
import anygui

log('The current backend is:', backend())
log("No output below this line indicates success")
assert backend() in anygui._backends
