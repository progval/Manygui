from anygui import *
from anygui.Utils import log

app = Application()

w1 = Window(title='', size=(200,100), visible=0)
app.add(w1)

lab = Label(text='Hello, world!', position=(30, 30))

w1.add(lab)

w2 = Window(title='This Window is visible', size=(200, 100))
app.add(w2)

def show(*args, **kw):
    w1.visible = 1

b = Button(text='Show other window', position=(5, 5),
           size=(190, 90))
link(b, show)

w2.add(b)

app.run()
