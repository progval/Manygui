# Lame but functional Tic-Tac-Toe game using Anygui.
# This version demonstrates the use of the SimpleGridManager,
# a layout manager approximately equivalent to Java's
# GridLayout.

from anygui import Window, Label, Application, Button, Frame, link
from anygui.LayoutManagers import SimpleGridManager, SimpleGridException
from random import uniform

# The "strategy" is to let the user (X) go first, and then
# place an O at random. The most interesting way to play this
# game is to try to let the machine win :-)

btns = []

rows = [[0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]]

def allBoxesFilled():
    n = 0
    for i in range(0,9):
       if btns[i].text != "": n += 1
    if n == 9: return 1

def rowOf(xo):
    for bs in rows:
        n = 0
        for b in bs:
            if btns[b].text == xo:
                n += 1
        if n == 3:
            return bs

def doAgain(*args,**kws):
    for i in range(0,9):
        btns[i].text = ""
    l1.text = "Your move..."

def makeMove(btn):
    def do_move(btn=btn,**kws):
        doMove(btn)
    return do_move

def highlightRow(row):
    for i in row:
        c = btns[i].text
        if c == 'x': c = 'X'
        if c == 'o': c = 'O'
        btns[i].text = c

def checkWin():
    row = rowOf('x')
    if row:
        highlightRow(row)
        l1.text = "You win!"
        return 1

    row = rowOf('o')
    if row:
        highlightRow(row)
        l1.text = "I win!"
        return 1

    if allBoxesFilled():
        l1.text = "Draw!"
        return 1

def doMove(the_btn = -1):
    if the_btn == -1:
        print "Something's wrong..."
        return

    btns[the_btn].text = 'x'
    btns[the_btn]._ensure_text()
    if checkWin():
        return

    l1.text = "Thinking..."
    b = int(uniform(0,9))
    while btns[b].text != "":
        b = int(uniform(0,9))
    btns[b].text = "o"

    if checkWin():
        return

    l1.text = "Your move..."

app = Application()

win = Window(width = 160, height = 250)
win.layout = SimpleGridManager(3,4)

b1 =  Button(height = 32, width=32, text = "")
link(source=b1, event='action', handler = makeMove(0))
b2 =  Button(height = 32, width=32, text = "")
link(source=b2, event='action', handler = makeMove(1))
b3 =  Button(height = 32, width=32, text = "")
link(source=b3, event='action', handler = makeMove(2))
b4 =  Button(height = 32, width=32, text = "")
link(source=b4, event='action', handler = makeMove(3))
b5 =  Button(height = 32, width=32, text = "")
link(source=b5, event='action', handler = makeMove(4))
b6 =  Button(height = 32, width=32, text = "")
link(source=b6, event='action', handler = makeMove(5))
b7 =  Button(height = 32, width=32, text = "")
link(source=b7, event='action', handler = makeMove(6))
b8 =  Button(height = 32, width=32, text = "")
link(source=b8, event='action', handler = makeMove(7))
b9 =  Button(height = 32, width=32, text = "")
link(source=b9, event='action', handler = makeMove(8))

# A frame for the controls:
b10 = Button(height = 32, width=32, text = "Play Again",geometry = (10,10,100,50))
link(source=b10,event='action', handler=doAgain)
l1 =  Label(height = 32, text = "Your move...",geometry=(10,70,100,50))
f = Frame()
f.layout = SimpleGridManager()

btns = [b1,b2,b3,b4,b5,b6,b7,b8,b9]

win.add(b1,b2,b3,b4,b5,b6,b7,b8,b9)
win.add(f,row=3,col=0,colspan=3)
f.add(b10,insets=(5,2))
f.add(l1,insets=(5,5))
#f.add(b10,l1)

app.run()
