from anygui import *

app = Application()

g_y = 150

win = Window(width = 110, height = 210)
app.add(win)
newbtn = None

def printit1(**ignore_kwds):
    return
    print 'printit1:',newbtn.text

def printit2(**ignore_kwds):
    return
    print 'printit2:',newbtn.text

def say_hello(**kw):
    #print "Hello, world!"
    global newbtn
    if newbtn is None:
        newbtn = TextField(opt, y = g_y)
        newbtn.text = TextModel('new')
        link(newbtn, printit1)
        link(newbtn.text, printit2)
        win.add(newbtn)
    else:
        newbtn.text.append('x')

opt = Options(x = 30, width = 50, height = 30)
btn = Button(opt, y = 30, text = "Hello")
link(btn, say_hello)
dis = Button(opt, y = 90, text = "Goodbye", enabled = 0)
link(dis, say_hello)

win.add(btn)
win.add(dis)

app.run()
