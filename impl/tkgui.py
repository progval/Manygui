''' Dummy implementation of a Tkinter backend to
    demonstrate the import magic.
'''

viable = 0
try:
   from Tkinter import *
   viable = 1
except:
   pass

class Window(Tk):
    'Dummy implementation'
    def __init__(self, title):
        Tk.__init__(self)
