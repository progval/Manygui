from anygui import *
from anygui.backends.genericgui import AboutDialog

app = Application()
aboutAg = AboutDialog()
app.add(aboutAg)
app.run()
