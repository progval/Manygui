# Curses magic...
import curses

_debug_messages = 1
if _debug_messages:
    _f = open("curses.txt","w")

_cur_scr = None

_ox=0
_oy=0

ATTR_NORMAL = curses.A_NORMAL
ATTR_UNDERLINE = curses.A_UNDERLINE

def dbg(*msg):
    if not _debug_messages: return
    for m in msg:
        _f.write("%s %s"%(m,','))
    _f.write("\n")
    _f.flush()

def addstr(x,y,ch,n=0,attr=curses.A_NORMAL):
    #dbg("adding at %s,%s: <%s>"%(x,y,ch))
    if n == 0: n = len(ch)
    n = min(n,len(ch))
    for xx in range(0,n):
        addch(y,x+xx,ord(ch[xx]),attr)
    
def erase(x,y,w,h):
    #dbg("Erasing %s,%s,%s,%s"%(x,y,w,h))
    x-=_ox
    y-=_oy
    x = max(0,x)
    ex = min(_xsize,x+w)
    y = max(y,0)
    ey = min(_ysize,y+h)
    if ex <= x: return
    if ey <= y: return
    line = ' '*(ex-x)
    #dbg("Erasing %s,%s,%s,%s"%(x,y,ex,ey))
    for yy in range(y,ey-1):
        _cur_scr.addstr(yy,x,line)
    if ey == _ysize and ex == _xsize:
        line = line[:-1]
    _cur_scr.addstr(ey-1,x,line)
    
def addch(y,x,ch,attr=ATTR_NORMAL):
    x-=_ox
    y-=_oy
    if x<0 or y<0 or x>=_xsize or y>=_ysize:
        return
    if x==_xsize-1 and y==_ysize-1:
        # Can't address lower-right corner?
        return
    try:
        _cur_scr.addch(y,x,ch,attr)
    except:
        dbg("Exception addch",x,y)
    
def refresh():
    _cur_scr.refresh()
    
def erase_all():
    _cur_scr.erase()
    
def scr_quit():
    global _cur_scr, _inited
    if not _inited:
        return
    _cur_scr.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.noraw()
    curses.endwin()
    _inited = 0
    
_inited = 0
_xsize = 80
_ysize = 24
def scr_init():
    global _cur_scr, _inited, _xsize, _ysize
    if _inited:
        return
    _inited = 1
    _cur_scr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.raw()
    #_cur_scr.keypad(1)
    _ysize, _xsize = _cur_scr.getmaxyx()
    dbg("xsize",_xsize,"; ysize",_ysize)
    
    global SCR_LVLINE
    SCR_LVLINE = curses.ACS_VLINE
    global SCR_RVLINE
    SCR_RVLINE = curses.ACS_VLINE
    global SCR_UHLINE
    SCR_UHLINE = curses.ACS_HLINE
    global SCR_LHLINE
    SCR_LHLINE = curses.ACS_HLINE
    global SCR_ULCORNER
    SCR_ULCORNER = curses.ACS_ULCORNER
    global SCR_URCORNER
    SCR_URCORNER = curses.ACS_URCORNER
    global SCR_LLCORNER
    SCR_LLCORNER = curses.ACS_LLCORNER
    global SCR_LRCORNER
    SCR_LRCORNER = curses.ACS_LRCORNER

def move_cursor(x,y):
    x-=_ox
    y-=_oy
    #dbg("Moving cursor",x,y)
    if x<0 or y<0 or x>=_xsize or y >= _ysize:
        return
    if x==_xsize-1 and y==_ysize-1:
        # Can't address lower-right corner?
        return
    _cur_scr.move(y,x)
    
def get_char():
    return _cur_scr.getch()


def get_origin(): return _ox,_oy

def set_origin(ox,oy):
    global _ox, _oy
    _ox = ox
    _oy = oy
