from anygui import Window, Label, Button, TextArea
from anygui import link

ABOUT_TEXT="""
The purpose of the Anygui project is to create an easy-to-use, simple, \
and generic module for making graphical user interfaces in Python. \
Its main feature is that it works transparently with many different \
GUI packages on most platforms.
"""

class AboutDialog(Window):

    def __init__(self):
        Window.__init__(self, title='About Anygui', geometry=(250, 200, 300, 225))
        self.initWidgets()

    def initWidgets(self):
        #self.layout = SimpleGridManager(1,3)
        self.label = Label(text="Anygui info:")
        self.add(self.label, left=10, top=10)
        self.txtAbout = TextArea(text=ABOUT_TEXT, enabled=0)
        self.add(self.txtAbout, left=10, right=10, top=(self.label,5), \
                 bottom=45, hstretch=1, vstretch=1)
        self.btnOK = Button(text="OK")
        self.add(self.btnOK, right=10, bottom=10, hmove=1, vmove=1)
        link(self.btnOK, self.close)

    def close(self, event):
        self.destroy()
