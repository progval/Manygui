
# NOTE: This demonstration should not be expected to work
#       in release 0.1

from manygui import *
from manygui.Utils import log
from manygui.Colors import *

# Only javagui implements this so far:
#from manygui.backends.javagui import Canvas
#from manygui.backends.tkgui import Canvas
#from manygui.backends.txtutils.txtgui import Canvas

app = Application()
win = Window(size=(300,320),title="Iterated Function System Viewer")
app.add(win)
cvs = Canvas(geometry=(10,10,280,200))
win.add(cvs,row=0,col=0,colspan=3)

win.add(Label(geometry=(10,220,80,40),text="Functions:"))
expfield = TextField(geometry=(90,220,190,40),
                     text="x,y=x/2+100,y/2;x,y=x/2,y/2+100;x,y=x/2,y/2")
win.add(expfield)

win.add(Label(geometry=(10,270,80,40),text="Iterations:"))
iterfield = TextField(geometry=(90,270,160,40),text="1000")
win.add(iterfield)

import random
def draw_ifs(*args,**kws):
    cvs.drawPolygon([(0,0),(260,0),(260,200),(0,260)],closed=1,fillColor=white,edgeColor=white)
    funcs = expfield.text.split(';')
    x,y = 200,200
    iters = int(iterfield.text)
    for nn in range(iters):
        r = int(random.uniform(0,len(funcs)))
        exec(funcs[r])
        if nn<100: continue
        cvs.drawLine(x,y,x+1,y)

draw = Button(geometry=(250,270,40,40),text="Draw")
link(draw,draw_ifs)
win.add(draw)

app.run()
