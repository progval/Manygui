from anygui import *

class MyWindow(Window):
    pass

win = MyWindow(title = "A Standard Window",
	     width = 300, height = 200)
win.show()
print application()._windows
print win
print

dlog = Window(title = "A Dialog Window", style = 'dialog',
	      x = 100, y = 300, width = 300, height = 200)
dlog.show()
print application()._windows

application().run()

print application()._windows
