from anygui import *

app = Application()

g_y = 150

win = Window(width = 200, height = 300)

def say_hello(**kw):
    #print "Hello, world!"
    global g_y
    #btn = Button(opt, y = g_y, text="New")
    btn = Button(geometry = (30,g_y,50,30))
    g_y += 5
    win.add(btn)

opt = Options(x = 30, width = 50, height = 30)
btn = Button(opt, y = 30, text = "Hello")
link(btn, say_hello)
dis = Button(opt, y = 90, text = "Goodbye", enabled = 0)
link(dis, say_hello)

win.add(btn)
win.add(dis)

app.run()
