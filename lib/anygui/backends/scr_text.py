# Curses magic simulated on dumb console.

from anygui.backends import *
from anygui.Exceptions import Error

__all__ = anygui.__all__

from anygui.Utils import flatten
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

_f = open("txt.txt","w")
_debug_messages = 1
def dbg(msg):
    if not _debug_messages: return
    _f.write(msg+"\n")
    _f.flush()

# Screen buffer.
_line = [' ']*80

_scrbuf = []
for ii in range(0,23):
    _scrbuf.append(_line[:])
print len(_scrbuf)
print len(_scrbuf[0])

def addstr(x,y,ch,n=0,attr=0):
    dbg('addstr %s,%s,%s,%s'%(x,y,ch,n))
    global _scrbuf
    if n == 0: n = len(ch)
    n = min(n,len(ch))
    for xx in range(0,n):
        addch(y,x+xx,ord(ch[xx]))
    dbg("SCRBUF: %s"%_scrbuf)

def erase(x,y,w,h):
    dbg('erase %s,%s,%s,%s'%(x,y,w,h))
    global _scrbuf, _under_curs
    for y in range(y,y+h):
        _scrbuf[y][x:x+w] = [' ']*w
    if _cursx>=x and _cursx<x+w and _cursy>y and _cursy<y+w:
        _under_curs = ' '

def addch(y,x,ch):
    dbg('addch %s,%s,%s'%(x,y,ch))
    global _scrbuf, _under_curs
    _scrbuf[y][x] = chr(ch)
    if x==_cursx and y==_cursy: _under_curs = chr(ch)

def refresh():
    print join(reduce(op.add,_scrbuf),'')

def erase_all():
    _scrbuf = [' '*80]*23

def scr_quit():
    pass

def scr_init():
    pass

_cursx = 0
_cursy = 0
_under_curs = ' '
def move_cursor(x,y):
    global _under_curs, _cursx, _cursy
    if x==_cursx and y==_cursy: return
    _scrbuf[_cursy][_cursx] = _under_curs
    _under_curs = _scrbuf[y][x]
    _cursx = x
    _cursy = y
    _scrbuf[_cursy][_cursx] = '*'
    refresh()

_inbuf = ""
def get_char():
    global _inbuf
    if len(_inbuf) == 0:
        _inbuf = raw_input()
    c = _inbuf[0]
    _inbuf = _inbuf[1:]
    return ord(c)
