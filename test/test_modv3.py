from anygui import *
from anygui.Utils import log

newbtn = None

app = Application()

win = Window(width = 110, height = 210)

g_y = 150

app.add(win)

def printit1(event):
   	log('printit1:',newbtn.on)
		
def printit2(event):
   	log('printit2:',newbtn.on)
			
def say_hello(event):
    #log("Hello, world!")
    global newbtn, g_y, win
    if newbtn is None:
        newbtn = CheckBox(opt, y = g_y)
        newbtn.installOnModel(BooleanModel())
        link(newbtn, printit1)
        link(newbtn.on, printit2)
        win.add(newbtn)
    else:
        val = not bool(newbtn.on)
        newbtn.on = val
			
opt = Options(x = 30, width = 50, height = 30)
btn = Button(opt, y = 30, text = "Hello")
link(btn, say_hello)
			
win.add(btn)
			
app.run()
