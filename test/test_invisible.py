from anygui import *

app = Application()

w1 = Window(title='', size=(200,100), visible=0)

lab = Label(text='Hello, world!', position=(30, 30))

w1.place(lab)

w2 = Window(title='This Window is visible', size=(200, 100))

def show(**kw):
    w1.visible = 1

b = Button(text='Show other window', position=(5, 5),
           size=(190, 90))
link(b, show)

w2.place(b)

app.run()
