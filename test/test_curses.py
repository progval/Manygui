from anygui import *
import anygui
#import anygui.backends.cursesgui as cg

app = Application()

win = Window(title="Window 1")
app.add(win)
win.geometry=(10,10,400,200)

win.add(Label(text="^F focus; ^Q quit; space click",
              geometry=(30,30,300,30)))
b1_1 = Button(text="Click Me",
            geometry=(30,60,100,70))
lb1_1 = Label(text="Label 1",
            geometry=(150,60,200,30))
win.add(b1_1)
win.add(lb1_1)

def change_lb1_1(*args,**kws):
    if lb1_1.text != "Hello":
        lb1_1.text = "Hello"
    else:
        lb1_1.text = "World"
link(b1_1,change_lb1_1)

win2 = Window(title="Window 2")
app.add(win2)
win2.geometry=(100,250,400,200)

n = 0
b2_1 = Button(text="Cheshire",geometry=(30,60,100,70))
b2_2 = Button(text="0",geometry=(150,60,100,70))

def change_b2_2(*args,**kws):
    global n
    n += 1
    b2_2.text = "%d"%n

def toggle_b2_1(*args,**kws):
    if b2_1 in win2._contents:
        win2.remove(b2_1)
    else:
        win2.add(b2_1)

link(b2_1,change_b2_2)
link(b2_2,toggle_b2_1)

win2.add((b2_1,b2_2))



app.run()
