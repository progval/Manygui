from anygui import *

class MyWindow(Window):
    pass

app = Application()

win = MyWindow(title="A Standard Window",
               width=220, height = 150)
app.add(win)

def new_window(**kw):
    win = Window(title='Yay, another window!')
    app.add(win)

    # Test for flashing (should not be visible):
    for i in range(5):
        win.visible = not win.visible
    win.visible = 1
    
btn = Button(text='Create new window', size=(200,60), x=10, y=50)
link(btn, new_window)
win.add(btn)

print application()._windows
print

#dlog = Window(title = "A Dialog Window", style = 'dialog',
#	      x = 100, y = 300, width = 300, height = 200)

#print application()._windows

app.run()

print application()._windows
