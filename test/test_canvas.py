from anygui import *
from anygui.Colors import *

# Only javagui implements this so far:
#from anygui.backends.javagui import Canvas
from anygui.backends.tkgui import Canvas

app = Application()
win = Window(size=(300,300))
app.add(win)
cvs = Canvas(size=win.size)
win.add(cvs)

def click(x, y, **kw):
    print '[Mouse clicked at (%i, %i)]' % (x, y)
    if 30 <= x <= 100 and 30 <= y <= 100:
        print 'Yay! You clicked the round rect!'

link(cvs, 'click', click)

# Taken from http://piddle.sourceforge.net/sample1.html

cvs.defaultLineColor = Color(0.7,0.7,1.0)    # light blue
cvs.drawLines(map(lambda i:(i*10,0,i*10,300), range(30)))
cvs.drawLines(map(lambda i:(0,i*10,300,i*10), range(30)))
cvs.defaultLineColor = black         

cvs.drawLine(10, 200, 20, 190, color=red)
cvs.drawEllipse(130, 30, 200, 100, fillColor=yellow, edgeWidth=4)

cvs.drawArc(130, 30, 200, 100, 45, 50, fillColor=blue, edgeColor=navy, edgeWidth=4)

cvs.defaultLineWidth = 4
cvs.drawRoundRect(30, 30, 100, 100, fillColor=blue, edgeColor=maroon)
cvs.drawCurve(20, 20, 100, 50, 50, 100, 160, 160)

#cvs.drawString("This is a test!", 30,130, Font(face="times",size=16,bold=1), 
#                color=green, angle=-45)

polypoints = [(160,120), (130,190), (210,145), (110,145), (190,190)]
cvs.drawPolygon(polypoints, fillColor=lime, edgeColor=red, edgeWidth=3, closed=1)

cvs.drawRect(200, 200, 260, 260, edgeColor=yellow, edgeWidth=5)
cvs.drawLine(200, 260, 260, 260, color=green, width=5)
cvs.drawLine(260, 200, 260, 260, color=red, width=5)

#cvs.flush()

app.run()
