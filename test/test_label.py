from anygui import Window, Label, Application
from anygui.Utils import log

app = Application()

win = Window(width = 160, height = 100)
app.add(win)
lb1 = Label(x = 30, y = 18, height = 32, text = "Spam!")
lb2 = Label(x = 30, y = 58, height = 32, text = "Glorious Spam!")

win.add(lb1)
win.add(lb2)

app.run()
