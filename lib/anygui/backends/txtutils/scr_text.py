# Curses magic simulated on dumb console.

import os

_debug_messages = 1
if _debug_messages:
    _f = open("txt.txt","w")

def dbg(*msg):
    if not _debug_messages: return
    for m in msg:
        _f.write("%s %s"%(m,','))
    _f.write("\n")
    _f.flush()


from string import join
import operator as op

SCR_LVLINE = ord('|')
SCR_RVLINE = ord('|')
SCR_UHLINE = ord('-')
SCR_LHLINE = ord('-')
SCR_ULCORNER = ord('+')
SCR_URCORNER = ord('+')
SCR_LLCORNER = ord('+')
SCR_LRCORNER = ord('+')


ATTR_NORMAL = 0
ATTR_UNDERLINE = 0
ATTR_SELECTED = 0

# Screen buffer.
_xsize=80
_ysize=23

_ox=0
_oy=0

try:
    _xsize,_ysize=map(int,os.environ['SCREENSIZE'].split('x'))
    _ysize -= 1 # Leave room for the prompt line.
except KeyError:
    try:
        _xsize=int(os.environ['COLUMNS'])
        _ysize=int(os.environ['LINES'])
        _ysize -= 1 # Leave room for the prompt line.
    except KeyError:
        pass
#print 'x,y=',_xsize,_ysize
_line = [' ']*_xsize
_scrbuf = []
for ii in range(0,_ysize):
    _scrbuf.append(_line[:])

def addstr(x,y,ch,n=0,attr=0):
    if _inbuf!="":
        return
    #dbg('addstr %s,%s,%s,%s'%(x,y,ch,n))
    global _scrbuf
    if n == 0: n = len(ch)
    n = min(n,len(ch))
    for xx in range(0,n):
        addch(y,x+xx,ord(ch[xx]))
    #dbg("SCRBUF: %s"%_scrbuf)

def erase(x,y,w,h):
    if _inbuf!="":
        return
    x -= _ox
    y -= _oy
    #dbg('erase %s,%s,%s,%s'%(x,y,w,h))
    global _scrbuf, _under_curs
    ex = min(_xsize,x+w)
    x = max(0,x)
    ey = min(_ysize,y+h)
    y = max(y,0)
    if ex <= x: return
    if ey <= y: return
    w = ex-x
    for y in range(y,ey):
        _scrbuf[y][x:ex] = [' ']*w
    if _cursx>=x and _cursx<x+w and _cursy>y and _cursy<y+w:
        _under_curs = ' '

def addch(y,x,ch):
    if _inbuf!="":
        return
    x -= _ox
    y -= _oy
    #dbg('addch %s,%s,%s'%(x,y,ch))
    if x<0 or y<0 or x>=_xsize or y>=_ysize:
        return
    global _scrbuf, _under_curs
    _scrbuf[y][x] = chr(ch)
    if x==_cursx and y==_cursy: _under_curs = chr(ch)

def refresh():
    if _inbuf=="":
        print join(reduce(op.add,_scrbuf),'')

def erase_all():
    if _inbuf!="":
        return
    global _scrbuf
    _scrbuf = []
    for ii in range(0,_ysize):
        _scrbuf.append(_line[:])

def scr_quit():
    pass

def scr_init():
    pass

_cursx = 0
_cursy = 0
_under_curs = ' '
def move_cursor(x,y):
    x -= _ox
    y -= _oy
    if x<0 or y<0 or x>=_xsize or y >= _ysize:
        return
    global _under_curs, _cursx, _cursy
    _scrbuf[_cursy][_cursx] = _under_curs
    _under_curs = _scrbuf[y][x]
    _cursx = x
    _cursy = y
    _scrbuf[_cursy][_cursx] = '*'

_inbuf = ""
def get_char():
    global _inbuf
    if len(_inbuf) == 0:
        _inbuf = raw_input()
    try:
        c = _inbuf[0]
        _inbuf = _inbuf[1:]
    except:
        return ord('\n')
    return ord(c)

def get_origin(): return _ox,_oy

def set_origin(ox,oy):
    global _ox, _oy
    _ox = ox
    _oy = oy
