from anygui.backends.cursesgui import *

app = Application()

win = Window()
win.geometry = (10,10,40,10)

win2 = Window()
win2.geometry = (20,15,40,8)

fr1 = Frame(geometry=(3,3,20,4))
win2.add(fr1)

app.run()
