
from Components import Component
from Colors import *
from Fonts import *
import Defaults

figureLine = 1
figureArc = 2
figureCurve = 3

# FIXME: Should include "vcr" functionality, and use a call to
#        _ensure_graphics in backend.

class Canvas(Component, Defaults.Canvas):

    """This is the base class for a drawing canvas.  The backend
    canvases just inherit from this one, and implement the various
    drawing methods."""

    def __init__(self, *args, **kwds):
        '''Initialize the canvas, and set default drawing parameters. 
        Derived classes should be sure to call this method.'''
        Component.__init__(self, *args, **kwds)
        # defaults used when drawing
        self.defaultLineColor = black
        self.defaultFillColor = transparent
        self.defaultLineWidth = 1
        self.defaultFont = Font()

    def clear(self):
        "Call this to clear and reset the graphics context."
        raise NotImplementedError, 'clear'

    def drawLine(self, x1, y1, x2, y2, color=None, width=None):
        "Draw a straight line between x1,y1 and x2,y2."
        self.drawPolygon([(x1, y1), (x2, y2)],
                         edgeColor=color,
                         edgeWidth=width)

    def drawLines(self, lineList, color=None, width=None):
        "Draw a set of lines of uniform color and width.  \
        lineList: a list of (x1,y1,x2,y2) line coordinates."
        for x1, y1, x2, y2 in lineList:
            self.drawLine(x1, y1, x2, y2 ,color,width)

    def drawCurve(self, x1, y1, x2, y2, x3, y3, x4, y4, 
                  edgeColor=None, edgeWidth=None, fillColor=None, closed=0):
        "Draw a Bezier curve with control points x1,y1 to x4,y4."

        pointlist = curvePoints(x1, y1, x2, y2, x3, y3, x4, y4)
        self.drawPolygon(pointlist,
                         edgeColor=edgeColor,
                         edgeWidth=edgeWidth,
                         fillColor=fillColor, closed=closed)

    def drawRect(self, x1, y1, x2, y2, edgeColor=None, edgeWidth=None, fillColor=None):
        "Draw the rectangle between x1,y1, and x2,y2. \
        These should have x1<x2 and y1<y2."
		
        pointList = [ (x1,y1), (x2,y1), (x2,y2), (x1,y2) ]
        self.drawPolygon(pointList, edgeColor, edgeWidth, fillColor, closed=1)

    def drawRoundRect(self, x1, y1, x2, y2, rx=8, ry=8,
                      edgeColor=None, edgeWidth=None, fillColor=None):
        "Draw a rounded rectangle between x1,y1, and x2,y2, \
        with corners inset as ellipses with x radius rx and y radius ry. \
        These should have x1<x2, y1<y2, rx>0, and ry>0."

        x1, x2 = min(x1,x2), max(x1, x2)
        y1, y2 = min(y1,y2), max(y1, y2)
		
        dx = rx*2
        dy = ry*2
	
        partList = [
            (figureArc, x1, y1, x1+dx, y1+dy, 180, -90),
            (figureLine, x1+rx, y1, x2-rx, y1),
            (figureArc, x2-dx, y1, x2, y1+dy, 90, -90),
            (figureLine, x2, y1+ry, x2, y2-ry),
            (figureArc, x2-dx, y2, x2, y2-dy, 0, -90),
            (figureLine, x2-rx, y2, x1+rx, y2),
            (figureArc, x1, y2, x1+dx, y2-dy, -90, -90),
            (figureLine, x1, y2-ry, x1, y1+rx)
            ]

        self.drawFigure(partList, edgeColor, edgeWidth, fillColor, closed=1)

    def drawEllipse(self, x1, y1, x2, y2, edgeColor=None, edgeWidth=None, fillColor=None):
        "Draw an orthogonal ellipse inscribed within the rectangle x1,y1,x2,y2. \
        These should have x1<x2 and y1<y2."

        pointlist = arcPoints(x1, y1, x2, y2, 0, 360)
        self.drawPolygon(pointlist,edgeColor, edgeWidth, fillColor, closed=1)

    def drawArc(self, x1, y1, x2, y2, startAng=0, extent=360,
                edgeColor=None, edgeWidth=None, fillColor=None):
        "Draw a partial ellipse inscribed within the rectangle x1,y1,x2,y2, \
        starting at startAng degrees and covering extent degrees.   Angles \
        start with 0 to the right (+x) and increase counter-clockwise. \
        These should have x1<x2 and y1<y2."
		
        center = (x1+x2)/2, (y1+y2)/2
        pointlist = arcPoints(x1, y1, x2, y2, startAng, extent)
		
        # Fill...
        self.drawPolygon(pointlist+[center]+[pointlist[0]],
		         transparent, 0, fillColor)

        # Outline...
        self.drawPolygon(pointlist, edgeColor, edgeWidth, transparent)

    def drawPolygon(self, pointlist, 
                    edgeColor=None, edgeWidth=None, fillColor=None, closed=0):
        """drawPolygon(pointlist) -- draws a polygon
        pointlist: a list of (x,y) tuples defining vertices
        closed: if 1, adds an extra segment connecting the last point to the first
        """
        raise NotImplementedError, 'drawPolygon'
	
    def drawFigure(self, partList,
                   edgeColor=None, edgeWidth=None, fillColor=None, closed=0):
        """drawFigure(partList) -- draws a complex figure
        partlist: a set of lines, curves, and arcs defined by a tuple whose
        first element is one of figureLine, figureArc, figureCurve
        and whose remaining 4, 6, or 8 elements are parameters."""
	
        pointList = []
	
        for tuple in partList:
            op = tuple[0]
            args = list(tuple[1:])
            
            if op == figureLine:
                pointList.extend( [args[:2], args[2:]] )
            elif op == figureArc:
                pointList.extend(apply(arcPoints,args))
            elif op == figureCurve:
                pointList.extend(apply(curvePoints,args))
            else:
                raise TypeError, "unknown figure operator: "+op
	
            self.drawPolygon(pointList, edgeColor, edgeWidth, fillColor, closed=closed)

    """
    def drawImage(self, image, x1, y1, x2=None, y2=None):
        '''Draw a PIL Image into the specified rectangle.  If x2 and y2 are
        omitted, they are calculated from the image size.'''
        raise NotImplementedError, 'drawImage'

    def stringWidth(self, s, font=None):
        "Return the logical width of the string if it were drawn \
        in the current font (defaults to self.font)."
        raise NotImplementedError, 'stringWidth'
	
    def fontHeight(self, font=None):
        "Find the height of one line of text (baseline to baseline) of the given font."
        # the following approxmation is correct for PostScript fonts,
        # and should be close for most others:
        if not font: font = self.defaultFont
        return 1.2 * font.size
		
    def fontAscent(self, font=None):
        "Find the ascent (height above base) of the given font."
        raise NotImplementedError, 'fontAscent'
    
    def fontDescent(self, font=None):
        "Find the descent (extent below base) of the given font."
        raise NotImplementedError, 'fontDescent'
    
    def drawMultiLineString(self, s, x, y, font=None, color=None, angle=0):
        "Breaks string into lines (on \n, \r, \n\r, or \r\n), and calls drawString on each."
        import math
        import string
        h = self.fontHeight(font)
        dy = h * math.cos(angle*math.pi/180.0)
        dx = h * math.sin(angle*math.pi/180.0)
        s = string.replace(s, '\r\n', '\n')
        s = string.replace(s, '\n\r', '\n')
        s = string.replace(s, '\r', '\n')
        lines = string.split(s, '\n')
        for line in lines:
            self.drawString(line, x, y, font, color, angle)
            x = x + dx
            y = y + dy

    def drawString(self, s, x, y, font=None, color=None, angle=0):
        "Draw a string starting at location x,y."
        # NOTE: the baseline goes on y; drawing covers (y-ascent,y+descent)
        raise NotImplementedError, 'drawString'

    """

# Utility functions

# FIXME: Seems to be incorrect...
def arcPoints(x1,y1, x2,y2, startAng=0, extent=360):
    "Return a list of points approximating the given arc."		
    # Note: this implementation is simple and not particularly efficient.
    xScale = abs((x2-x1)/2.0)
    yScale = abs((y2-y1)/2.0)
	
    x = min(x1,x2)+xScale
    y = min(y1,y2)+yScale
    
    # "Guesstimate" a proper number of points for the arc:
    steps = min(max(xScale,yScale)*(extent/10.0)/10,200)
    if steps < 5: steps = 5
        
    from math import sin, cos, pi
	
    pointlist = []
    step = float(extent)/steps
    angle = startAng
    for i in range(int(steps+1)):
        point = (x+xScale*cos((angle/180.0)*pi),
                 y-yScale*sin((angle/180.0)*pi))
        pointlist.append(point)
        angle = angle+step
	
    return pointlist
    
def curvePoints(x1, y1, x2, y2, x3, y3, x4, y4):
    "Return a list of points approximating the given Bezier curve."
    
    # Adapted from BEZGEN3.HTML, one of the many
    # Bezier utilities found on Don Lancaster's Guru's Lair at
    # <URL: http://www.tinaja.com/cubic01.html>	
    bezierSteps = min(max(max(x1,x2,x3,x4)-min(x1,x2,x3,x3),
                          max(y1,y2,y3,y4)-min(y1,y2,y3,y4)),
                      200)
	
    dt1 = 1. / bezierSteps
    dt2 = dt1 * dt1
    dt3 = dt2 * dt1
	
    xx = x1
    yy = y1
    ux = uy = vx = vy = 0
	
    ax = x4 - 3*x3 + 3*x2 - x1
    ay = y4 - 3*y3 + 3*y2 - y1
    bx = 3*x3 - 6*x2 + 3*x1
    by = 3*y3 - 6*y2 + 3*y1
    cx = 3*x2 - 3*x1
    cy = 3*y2 - 3*y1
	
    mx1 = ax * dt3
    my1 = ay * dt3
	
    lx1 = bx * dt2
    ly1 = by * dt2
    
    kx = mx1 + lx1 + cx*dt1
    ky = my1 + ly1 + cy*dt1
	
    mx = 6*mx1 
    my = 6*my1
	
    lx = mx + 2*lx1
    ly = my + 2*ly1
	
    pointList = [(xx, yy)]
	
    for i in range(bezierSteps):
        xx = xx + ux + kx
        yy = yy + uy + ky
        ux = ux + vx + lx
        uy = uy + vy + ly
        vx = vx + mx
        vy = vy + my
        pointList.append((xx, yy)) 
	
    return pointList
