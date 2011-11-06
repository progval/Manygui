# Lame but functional Tic-Tac-Toe game using Anygui.
# This version demonstrates the use of the GridManager,
# a layout manager with approximately the same functionality
# as Java's GridBagLayout or Tk's "grid" manager. Compared
# to ttt.py, this version makes the board expand while
# keeping the height of the button and label at the
# bottom constant. It also fiddles with the relative
# size and expansion of the board rows and columns, just
# for fun.

from anygui import Window, Label, Application, Button, link
from anygui.LayoutManagers import GridManager, GridException
from anygui.Utils import Options
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
        print("Something's wrong...")
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

win = Window(width = 250, height = 450)
win.layout = GridManager(3)

b1 =  Button(height = 32, width=32, text = "")
link(b1,makeMove(0))
b2 =  Button(height = 32, width=32, text = "")
link(b2,makeMove(1))
b3 =  Button(height = 32, width=32, text = "")
link(b3,makeMove(2))
b4 =  Button(height = 32, width=32, text = "")
link(b4,makeMove(3))
b5 =  Button(height = 32, width=32, text = "")
link(b5,makeMove(4))
b6 =  Button(height = 32, width=32, text = "")
link(b6,makeMove(5))
b7 =  Button(height = 32, width=32, text = "")
link(b7,makeMove(6))
b8 =  Button(height = 32, width=32, text = "")
link(b8,makeMove(7))
b9 =  Button(height = 32, width=32, text = "")
link(b9,makeMove(8))
b10 = Button(height = 32, width=32, text = "Play Again")
link(b10,doAgain)
l1 =  Label(height = 32, text = "Your move...")

btns = [b1,b2,b3,b4,b5,b6,b7,b8,b9]

# You can add components either to the layout or to the
# Window, the result is the same:
opt = Options(xweight=1,yweight=1,row=0,col=0,colspan=1)
win.add((b1,b2,b3),opt,row=0)
win.layout.add((b4,b5,b6),opt,row=1)
win.add((b7,b8,b9),opt,row=2)
win.layout.add(b10,row=3,col=0,colspan=3,insets=(20,2),yweight=0)
win.add(l1,row=4,col=0,colspan=2,insets=(20,2),yweight=0)

# Calling add() with no items lets you configure rows
# and columns.
#win.add(col=0,xweight=0)
#win.layout.add(col=2,xweight=0)
#win.layout.add(row=1,yweight=0.5)
#win.add(row=1,minheight=100)

app.run()
