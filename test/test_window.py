from anygui import *
from anygui.Utils import log

class MyWindow(Window):
    pass

app = Application()

win = MyWindow(title="A Standard Window",
               width=220, height = 45)
app.add(win)

def new_window(**kw):
    win = Window(title='Yay, another window!')

    # Test for flashing (should not be visible):
    for i in range(5):
        win.visible = not win.visible
    win.visible = 1

    # win.open()
    app.add(win)
    
btn = Button(text='Create new window', size=(200,25), x=10, y=10)
link(btn, new_window)
win.add(btn)

log(application()._windows)
#print
log("")

#dlog = Window(title = "A Dialog Window", style = 'dialog',
#	      x = 100, y = 300, width = 300, height = 200)

#log(application()._windows)

app.run()

log(application()._windows)
