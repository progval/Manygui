# Curses magic...
import curses

_f = open("curses.txt","w")
_debug_messages = 1

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
    try:
        if n != 0:
            _scr.addnstr(y,x,ch,n,attr)
        else:
            _scr.addstr(y,x,ch,attr)
    except:
        raise CursesGUIException(value="addstr/addnstr error: %d,%d <- \"%s\""%(x,y,ch))

def erase(x,y,w,h):
    #dbg("Erasing %s,%s,%s,%s"%(x,y,w,h))
    for xx in range(x,x+w):
        for yy in range(y,y+h):
            addstr(xx,yy,' ')        

def addch(y,x,ch):
    _scr.addch(y,x,ch)

def refresh():
    _scr.refresh()

def erase_all():
    _scr.erase()

def scr_quit():
    _scr.keypad(1)
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
    _ysize, _xsize = _scr.getmaxyx()

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
    _scr.move(y,x)

def get_char():
    return _scr.getch()
