from anygui import *
from anygui.Utils import log

app = Application()

win = Window(title="Window 1")
win.geometry=(10,10,360,250)
app.add(win)

win2 = Window(title="Window 2")
win2.geometry=(30,130,400,200)
app.add(win2)
# Test...

lb1 = Label(geometry=(10,10,100,30),text="Label 1")
win.add(lb1)

def change_lb1(*args,**kws):
    if lb1.text != "Hello":
        lb1.text = "Hello"
    else:
        lb1.text = "World"

b1 = Button(geometry=(110,10,100,30),text="Click Me")
link(b1,change_lb1)
win.add(b1)

rg = RadioGroup()
rb1 = RadioButton(geometry=(10,50,120,30),text="Choose me!",group=rg,value=1)
rb2 = RadioButton(geometry=(10,90,120,30),text="No, choose me!",group=rg,value=2)
rb3 = RadioButton(geometry=(10,130,120,30),text="No, me!",group=rg,value=3)
win.add(rb1)
win.add(rb2)
win.add(rb3)


b2, b3 = Button(geometry=(10,10,120,30),text="A button"), Button(geometry=(150,10,120,30),text="Button 0")

n = 0
def change_b3(*args,**kws):
    global n
    n += 1
    b3.text = "Button %d"%n
link(b2,change_b3)

def toggle_b2(*args,**kws):
    if b2 in win2._contents:
        win2.remove(b2)
    else:
        win2.add(b2)
link(b3,toggle_b2)

win2.add(b2)
win2.add(b3)

fr = Frame(geometry=(10,40,350,130))
win2.add(fr)
cb1 = CheckBox(geometry=(10,10,80,30),text="Option 1")
cb2 = CheckBox(geometry=(10,50,80,30),text="Option 2")
cb3 = CheckBox(geometry=(10,90,80,30),text="Option 3")
ta = TextArea(geometry=(100,10,240,110),text="Now is the time for all good\npersons...")
fr.add(cb1)
fr.add(cb2)
fr.add(cb3)
fr.add(ta)

app.run()
