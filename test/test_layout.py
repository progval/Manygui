from anygui import *

# Tests stretching when distances are zero

app = Application()

btn = Button(text='Hello')

win = Window(size=(200,100))
win.add(btn, left=0, top=0, right=0, bottom=0, hstretch=1, vstretch=1)

app.add(win)

app.run()

