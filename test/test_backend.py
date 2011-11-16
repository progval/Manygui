from manygui import backend
from manygui.Utils import log
import manygui

log('The current backend is:', backend())
log("No output below this line indicates success")
assert backend() in manygui._backends
