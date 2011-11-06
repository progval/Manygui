from anygui import *
from anygui.Utils import log

class MyWindow(Window):
    pass

app = Application()

win = MyWindow(title="A Standard Window",
               x=50, y=50, width=220, height=45)
app.add(win)

def new_window(event):
    win = Window(title='Yay, another window!', x=100, y=100)

    # Test for flashing (should not be visible):
    for i in range(100):
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
