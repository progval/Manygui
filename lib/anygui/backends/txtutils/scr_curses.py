# Curses magic...
import curses

_debug_messages = 0
if _debug_messages:
    _f = open("curses.txt","w")

_cur_scr = None

class Screen:
    ATTR_NORMAL = curses.A_NORMAL
    ATTR_UNDERLINE = curses.A_UNDERLINE

    def dbg(*msg):
        if not _debug_messages: return
        for m in msg:
            _f.write("%s %s"%(m,','))
        _f.write("\n")
        _f.flush()

    def addstr(self,x,y,ch,n=0,attr=curses.A_NORMAL):
        #dbg("adding at %s,%s: <%s>"%(x,y,ch))
        if n == 0: n = len(ch)
        n = min(n,len(ch))
        for xx in range(0,n):
            self.addch(y,x+xx,ord(ch[xx]),attr)
    
    def erase(self,x,y,w,h):
        #dbg("Erasing %s,%s,%s,%s"%(x,y,w,h))
        x = max(0,x)
        ex = min(self._xsize,x+w)
        y = max(y,0)
        ey = min(self._ysize,y+h)
        if ex <= x: return
        if ey <= y: return
        line = ' '*(ex-x)
        #dbg("Erasing %s,%s,%s,%s"%(x,y,ex,ey))
        for yy in range(y,ey-1):
            _cur_scr.addstr(yy,x,line)
        if ey == self._ysize and ex == self._xsize:
            line = line[:-1]
        _cur_scr.addstr(ey-1,x,line)
    
    def addch(self,y,x,ch,attr=ATTR_NORMAL):
        if x<0 or y<0 or x>=self._xsize or y>=self._ysize:
            return
        if x==self._xsize-1 and y==self._ysize-1:
            # Can't address lower-right corner?
            return
        try:
            _cur_scr.addch(y,x,ch,attr)
        except:
            self.dbg("Exception addch",x,y)
    
    def refresh(self):
        _cur_scr.refresh()
    
    def erase_all(self):
        _cur_scr.erase()
    
    def scr_quit(self):
        _cur_scr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.noraw()
        curses.endwin()
    
    _inited = 0
    _xsize = 80
    _ysize = 24
    def scr_init(self):
        global _cur_scr, _inited
        if Screen._inited:
            return
        Screen._inited = 1
        _cur_scr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.raw()
        _cur_scr.keypad(1)
        self._ysize, self._xsize = _cur_scr.getmaxyx()
        self.dbg("xsize",self._xsize,"; ysize",self._ysize)
    
        self.SCR_LVLINE = curses.ACS_VLINE
        self.SCR_RVLINE = curses.ACS_VLINE
        self.SCR_UHLINE = curses.ACS_HLINE
        self.SCR_LHLINE = curses.ACS_HLINE
        self.SCR_ULCORNER = curses.ACS_ULCORNER
        self.SCR_URCORNER = curses.ACS_URCORNER
        self.SCR_LLCORNER = curses.ACS_LLCORNER
        self.SCR_LRCORNER = curses.ACS_LRCORNER
    
    def move_cursor(self,x,y):
        #self.dbg("Moving cursor",x,y)
        if x<0 or y<0 or x>=self._xsize or y >= self._ysize:
            return
        if x==self._xsize-1 and y==self._ysize-1:
            # Can't address lower-right corner?
            return
        _cur_scr.move(y,x)
    
    def get_char(self):
        return _cur_scr.getch()

