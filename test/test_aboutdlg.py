from manygui import *
from manygui.backends.genericgui import AboutDialog

app = Application()
aboutAg = AboutDialog()
app.add(aboutAg)
app.run()
