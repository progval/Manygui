from anygui import Window, Label, Application

app = Application()

win = Window(width = 160, height = 100)
lbl = Label(x = 30, y = 30, height = 32, text = "Spam!\nGlorious Spam!")
win.add(lbl)

app.run()
