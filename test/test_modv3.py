from anygui import *

app = Application()

g_y = 150

win = Window(width = 110, height = 210)
app.add(win)
newbtn = None

def printit1(**ignore_kwds):
    print 'printit1:',newbtn.on,ignore_kwds

def printit2(**ignore_kwds):
    print 'printit2:',newbtn.on,ignore_kwds

def say_hello(**kw):
    print "Hello, world!"
    global newbtn
    if newbtn is None:
        newbtn = CheckBox(opt, y = g_y)
        newbtn.on = BooleanModel()
        link(newbtn, printit1)
        link(newbtn.on, printit2)
        win.add(newbtn)
    else:
        newbtn.on = not newbtn.on

opt = Options(x = 30, width = 50, height = 30)
btn = Button(opt, y = 30, text = "Hello")
link(btn, say_hello)

win.add(btn)

app.run()

