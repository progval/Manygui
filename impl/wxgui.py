''' Dummy implementation of a wxPython backend to
    demonstrate the import magic.
'''

viable = 0
try:
   from wxPython.wx import *
   viable = 1
except:
   pass

class Window(wxFrame):
    'Dummy implementation'
    def __init__(self, title):
        wxFrame.__init__(self, None, -1, title)
