from anygui import Window, Button, Application, Options

app = Application()

def say_hello():
    print "Hello, world!"

win = Window(width = 110, height = 150)

opt = Options(x = 30, width = 50, height = 30, action = say_hello)
btn = Button(opt, y = 30, text = "Hello")
dis = Button(opt, y = 90, text = "Goodbye", enabled = 0)

win.add(btn)
win.add(dis)
win.show()

app.run()
