from anygui import Window, Label, Application

app = Application()

win = Window(width = 160, height = 100)
lb1 = Label(x = 30, y = 30, height = 32, text = "Spam!")
lb2 = Label(x = 30, y = 48, height = 32, text = "Glorious Spam!")

win.add(lb1)
win.add(lb2)

app.run()
