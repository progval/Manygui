# Curses magic...
import curses

_debug_messages = 1
if _debug_messages:
    _f = open("curses.txt","w")

def dbg(*msg):
    if not _debug_messages: return
    for m in msg:
        _f.write("%s %s"%(m,','))
    _f.write("\n")
    _f.flush()

ATTR_NORMAL = curses.A_NORMAL
ATTR_UNDERLINE = curses.A_UNDERLINE

_scr = None

def addstr(x,y,ch,n=0,attr=curses.A_NORMAL):
    #dbg("adding at %s,%s: <%s>"%(x,y,ch))
    if n == 0: n = len(ch)
    n = min(n,len(ch))
    for xx in range(0,n):
        addch(y,x+xx,ord(ch[xx]))

def erase(x,y,w,h):
    dbg("Erasing %s,%s,%s,%s"%(x,y,w,h))
    x = max(0,x)
    ex = min(_xsize,x+w)
    y = max(y,0)
    ey = min(_ysize,y+h)
    if ex <= x: return
    if ey <= y: return
    line = ' '*(ex-x)
    dbg("Erasing %s,%s,%s,%s"%(x,y,ex,ey))
    for yy in range(y,ey-1):
        _scr.addstr(yy,x,line)
    if ey == _ysize and ex == _xsize:
        line = line[:-1]
    _scr.addstr(ey-1,x,line)

def addch(y,x,ch):
    if x<0 or y<0 or x>=_xsize or y>=_ysize:
        return
    if x==_xsize-1 and y==_ysize-1:
        # Can't address lower-right corner?
        return
    try:
        _scr.addch(y,x,ch)
    except:
        dbg("Exception addch",x,y)

def refresh():
    _scr.refresh()

def erase_all():
    _scr.erase()

def scr_quit():
    _scr.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.noraw()
    curses.endwin()

_inited = 0
_xsize = 80
_ysize = 24
def scr_init():
    global _scr, _inited, _xsize, _ysize
    if _inited:
        return
    _inited = 1
    _scr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.raw()
    _scr.keypad(1)
    _ysize, _xsize = _scr.getmaxyx()
    dbg("xsize",_xsize,"; ysize",_ysize)

    global SCR_LVLINE
    global SCR_RVLINE
    global SCR_UHLINE
    global SCR_LHLINE
    global SCR_ULCORNER
    global SCR_URCORNER
    global SCR_LLCORNER
    global SCR_LRCORNER

    SCR_LVLINE = curses.ACS_VLINE
    SCR_RVLINE = curses.ACS_VLINE
    SCR_UHLINE = curses.ACS_HLINE
    SCR_LHLINE = curses.ACS_HLINE
    SCR_ULCORNER = curses.ACS_ULCORNER
    SCR_URCORNER = curses.ACS_URCORNER
    SCR_LLCORNER = curses.ACS_LLCORNER
    SCR_LRCORNER = curses.ACS_LRCORNER

def move_cursor(x,y):
    dbg("Moving cursor",x,y)
    if x<0 or y<0 or x>=_xsize or y >= _ysize:
        return
    if x==_xsize-1 and y==_ysize-1:
        # Can't address lower-right corner?
        return
    _scr.move(y,x)

def get_char():
    return _scr.getch()
