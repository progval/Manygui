from anygui import Window, Button, Application

app = Application()

def say_hello():
    print "Hello, world!"

win = Window(width = 110, height = 150)
btn = Button(x = 30, y = 30, width = 50, height = 30, text = "Hello",
		 action = say_hello)
dis = Button(x = 30, y = 90, width = 50, height = 30, text = "Goodbye",
		 action = say_hello, enabled = 0)

win.add(btn)
win.add(dis)
win.show()

app.run()
