from anygui import *
from anygui.Utils import log
app = Application()
win = Window(width = 100, height = 100)
app.add(win)

def add_btn(**kws):
    win.add(b2)

def remove_btn(**kws):
    win.remove(b2)

b = Button(geometry=(10,10,50,32),text="Add")
link(b,add_btn)
b2 = Button(geometry=(10,50,70,32),text="Remove")
link(b2,remove_btn)

win.add(b)
app.run()
