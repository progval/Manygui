from anygui.backends.cursesgui import *

app = Application()

win = Window(geometry=(10,10,40,10),title="Window 1")
win.geometry=(10,5,40,8)

win2 = Window(geometry=(20,15,40,8),title="Window 2")
win2.geometry=(20,15,40,8)

lb1 = Label(geometry=(3,3,20,3),text="Label 1")
win2.add(lb1)

def change_lb1(*args,**kws):
    if lb1.text != "Hello":
        lb1.text = "Hello"
    else:
        lb1.text = "World"

b1 = Button(geometry=(24,3,10,3),text="Click Me")
link(b1,change_lb1)
win2.add(b1)

lb2 = Label(geometry=(1,1,36,3),text="f changes focus; q quits; c clicks")
b2, b3 = Button(geometry=(2,4,10,3),text="A button"), Button(geometry=(12,4,12,3),text="Button 0")

n = 0
def change_b3(*args,**kws):
    global n
    n += 1
    b3.text = "Button %d"%n
link(b2,change_b3)

win.add(b2)
win.add(b3)
win.add(lb2)

app.run()
