from anygui import *

app = Application()
bt1 = Button(text='Before')
bt2 = Button(text='Change')

def change(**kw):
    bt1.text = 'After'

link(bt2, change)

win = Window()
win.width = bt1.width*2 + 10
win.height = bt1.height
win.add((bt1, bt2))

app.run()
