from anygui.backends import *
import sys

__all__ = '''

  Application
  ButtonWrapper
  WindowWrapper
  LabelWrapper
  TextFieldWrapper
  TextAreaWrapper
  ListBoxWrapper
  RadioButtonWrapper

'''.split()

################################################################

import Tkinter, re
from anygui.Applications import AbstractApplication
from anygui.Wrappers import AbstractWrapper, DummyWidget, isDummy
from anygui.Events import *
from anygui import application

class Application(AbstractApplication):

    def __init__(self):
        AbstractApplication.__init__(self)
        self._root = Tkinter.Tk()
        self._root.withdraw()
    
    def internalRun(self):
        self._root.mainloop()

    def internalRemove(self):
        if not self._windows:
            self._root.destroy()

class Wrapper(AbstractWrapper):
    
    def __init__(self, *args, **kwds):
        AbstractWrapper.__init__(self, *args, **kwds)
        self.addConstraint('geometry', 'visible')
        # FIXME: Is this the right place to put it? Make sure
        # 'geometry' implies 'x', 'y', etc. too (see Wrappers.py)
        # Also, this scheme will cause flashing... (place before
        # place_forget)

    def enterMainLoop(self): # ...
        #if not isDummy(self.widget):
        #    self.widget.destroy()
        #    sys.stdout.flush()
        self.proxy.push() # FIXME: Why is this needed when push is called in internalProd (by prod)?
        
    def internalDestroy(self):
        self.widget.destroy()

# FIXME: It seems that layout stuff (e.g. hstretch and vmove) is set
# directly as state variables/attributes... Why is that? (There is a
# layout_data attribute too... Hm.)
class ComponentWrapper(Wrapper):

    def setX(self, x):
        self.widget.place(x=x)

    def setY(self, y):
        self.widget.place(y=y)

    def setWidth(self, width):
        self.widget.place(width=width)

    def setHeight(self, height):
        self.widget.place(height=height)

    def setPosition(self, x, y):
        self.widget.place(x=x, y=y)

    def setSize(self, width, height):
        self.widget.place(width=width, height=height)

    def setGeometry(self, x, y, width, height):
        self.widget.place(x=x, y=y, width=width, height=height)

    def setVisible(self, visible):
        if not visible: self.widget.place_forget()
        # Other case handled by geometric setters

    def setContainer(self, container):
        if container is None:
            try:
                self.destroy()
            except:
                pass
            return
        parent = container.wrapper.widget
        try:
            assert parent.isDummy()
        except (AttributeError, AssertionError):
            self.destroy()
            self.create(parent)
            self.proxy.push(blocked=['container'])

    def setEnabled(self, enabled):
        if enabled: newstate = Tkinter.NORMAL
        else: newstate = Tkinter.DISABLED
        try: self.widget.config(state=newstate)
        except Tkinter.TclError:
            # Widget doesn't support -state
            pass

    def setText(self,text):
        try:
            self.widget.configure(text=text)
        except:
            # Widget has no text.
            pass

    def getText(self):
        try:
            return self.widget.cget('text')
        except:
            # Widget has no text.
            return ""

class ButtonWrapper(ComponentWrapper):

    def clickHandler(self): 
        send(self.proxy, 'click')

    def setUp(self):
        self.widget.configure(command=self.clickHandler)

    def widgetFactory(self, *args, **kwds):
        return Tkinter.Button(*args, **kwds)

    def setText(self, text):
        self.widget.configure(text=text)

class LabelWrapper(ComponentWrapper):

    def widgetFactory(self,*args,**kws):
        return Tkinter.Label(*args,**kws)

    def setText(self, text):
        self.widget.configure(text=text)

class TkTextMixin:
    """ Mixin that abstracts out all behavior needed to get
    selectable-but-not-editable behavior out of Tk text widgets.
    We bind all keystrokes, passing them through to the underlying
    control when editable is true, and ignoring all but select
    and copy keystrokes when editable is false. The mixed-in
    class must provide an updateProxy() method, called as a
    Tk event handler when focus leaves the control; and a
    setEditable() method, called from update(), that manages
    the self.editable property. """

    def install_bindings(self,widget):
        self.ctl = 0
        self.alt = 0
        self.shift = 0
        self.editable = 1
        widget.bind("<Key>", self.keybinding)
        #widget.bind("<KeyRelease>",self.updateProxy) # Ensure all changes reach Proxy.
        widget.bind("<KeyPress-Control_L>", self.ctldown)
        widget.bind("<KeyRelease-Control_L>", self.ctlup)
        widget.bind("<KeyPress-Alt_L>", self.altdown)
        widget.bind("<KeyRelease-Alt_L>", self.altup)
        widget.bind("<KeyPress-Shift_L>", self.shiftdown)
        widget.bind("<KeyRelease-Shift_L>", self.shiftup)
        widget.bind("<Key-Insert>", self.insertbinding)
        widget.bind("<Key-Up>", self.arrowbinding)
        widget.bind("<Key-Down>", self.arrowbinding)
        widget.bind("<Key-Left>", self.arrowbinding)
        widget.bind("<Key-Right>", self.arrowbinding)
        widget.bind("<ButtonRelease>", self.insertbinding)

        # Easy place to put this - not _editable-related, but common
        # to all text widgets.
        #widget.bind("<Leave>", self.updateProxy)

    # Track modifier key state.
    def ctldown(self, ev):
        self.ctl = 1
    def ctlup(self, ev):
        self.ctl = 0
    def altdown(self, ev):
        self.alt = 1
    def altup(self, ev):
        self.alt = 0
    def shiftdown(self, ev):
        self.shift = 1
    def shiftup(self, ev):
        self.shift = 0

    def keybinding(self, ev):
        """ This method binds all keys, and causes them to be
        ignored when _editable is not set. """
        if self.editable:
            return None
        else:
            # This is truly horrid. Please add appropriate
            # code for Mac platform, someone.
            if (ev.char == "\x03") or (ev.char == "c" and self.alt):
                # DON'T ignore this key: it's a copy operation.
                return None
            return "break"

    def insertbinding(self,ev):
        # Overrides keybinding for the Insert key.
        if self.editable:
            return None
        if self.ctl:
            # Allow copy.
            return None
        return "break"

    def arrowbinding(self,ev):
        # This method's sole reason for existence is to allow arrows
        # to work even when self.editable is false.
        return None

class TextFieldWrapper(ComponentWrapper,TkTextMixin):

    def widgetFactory(self,*args,**kws):
        theWidge=Tkinter.Entry(*args,**kws)
        self.install_bindings(theWidge)
        return theWidge

    def updateProxy(self,*args,**kws):
        # Inform proxy of text change by the user.
        #self.proxy.rawModify(text=self.widget.get())
        #start,end = self.getSelection()
        #self.proxy.rawModify(selection=(start,end))
        pass

    def setText(self,text):
        disabled=0
        if self.widget.cget('state') != Tkinter.NORMAL:
            self.widget.configure(state=Tkinter.NORMAL)
            disabled=1
        self.widget.delete(0,Tkinter.END)
        self.widget.insert(0,text)
        if disabled:
            self.widget.configure(state=Tkinter.DISABLED)

    def getText(self):
        return self.widget.get()

    def setEditable(self,editable):
        self.editable=editable

    def setSelection(self,selection):
        self.widget.selection_range(*selection)

    def getSelection(self):
        if self.widget.select_present():
            start = self.widget.index('sel.first')
            end = self.widget.index('sel.last')
        else:
            start = end = self.widget.index('insert')
        return start,end

class ScrollableTextArea(Tkinter.Frame):

    # Replacement for Tkinter.Text

    _delegated_methods = """bind config cget get mark_names index delete insert
    mark_set tag_add tag_remove tag_names configure""".split()

    def __init__(self, *args, **kw):
        Tkinter.Frame.__init__(self, *args, **kw)
        
        self._yscrollbar = Tkinter.Scrollbar(self)
        self._yscrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)

        self._xscrollbar = Tkinter.Scrollbar(self, orient=Tkinter.HORIZONTAL)
        self._xscrollbar.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
        
        self._textarea = Tkinter.Text(self,
                                      yscrollcommand=self._yscrollbar.set,
                                      xscrollcommand=self._xscrollbar.set)
        self._textarea.pack(side=Tkinter.TOP, expand=Tkinter.YES, fill=Tkinter.BOTH)

        self._yscrollbar.config(command=self._textarea.yview)
        self._xscrollbar.config(command=self._textarea.xview)

        for delegate in self._delegated_methods:
            setattr(self, delegate, getattr(self._textarea, delegate))

class TextAreaWrapper(ComponentWrapper,TkTextMixin):

    def widgetFactory(self,*args,**kws):
        theWidge=ScrollableTextArea(*args,**kws)
        self.install_bindings(theWidge)
        return theWidge

    def getText(self):
        return self.widget.get(1.0, Tkinter.END)[:-1] # Remove the extra newline. (Always?)

    def _to_char_index(self, idx):
        # This is no fun, but there doesn't seem to be an easier way than
        # counting the characters in each line :-(   -- jak
        txt = self.widget
        idx = txt.index(idx)
        line, col = idx.split(".")
        line = int(line)
        tlen = 0
        for ll in range(1, line):
            tlen += len(txt.get("%s.0"%ll, "%s.end"%ll))
            tlen += 1
        tlen += int(col)
        return tlen

    def getSelection(self):
        try:
            start = self.widget.index('sel.first')
            end = self.widget.index('sel.last')
        except Tkinter.TclError:
            start = end = self.widget.index('insert')
            # Convert to character positions...
        # This could be more efficient if _to_char_index() took
        # multiple indexes and computed them all at once.
        start = self._to_char_index(start)
        end = self._to_char_index(end)
        return start, end

    def setText(self,text):
        disabled=0
        if self.widget.cget('state') != Tkinter.NORMAL:
            self.widget.config(state=Tkinter.NORMAL) # Make sure we can change the text
            disabled=1
        self.widget.delete(1.0, Tkinter.END)
        self.widget.insert(1.0, text)
        if disabled:
            self.widget.config(state=Tkinter.DISABLED)

    def setSelection(self,selection):
        start, end = selection
        self.widget.tag_remove('sel', '1.0', 'end')
        self.widget.tag_add('sel', '1.0 + %s char' % start, '1.0 + %s char' % end)

    def updateProxy(self,*args,**kws):
        # Ugh, we have to do this on every keystroke! I think
        # we may -really- need -some- kind of laziness.
        #self.proxy.rawModify(text=self.widget.get("1.0","end"))
        #start,end = self._getSelection()
        #self.proxy.rawModify(selection=(start,end))
        pass

    def setEditable(self,editable):
        self.editable=editable

class ListBoxWrapper(ComponentWrapper):

    def __init__(self,*args,**kws):
        ComponentWrapper.__init__(self,*args,**kws)
        self.items = []

    def widgetFactory(self,*args,**kws):
        theWidge=Tkinter.Listbox(*args,**kws)
        theWidge.bind('<ButtonRelease-1>', self._tk_clicked)
        theWidge.bind('<KeyRelease-space>', self._tk_clicked)
        return theWidge

    def setItems(self,items):
        self.widget.delete(0, Tkinter.END)
        self.items = items[:]
        for item in self.items:
            self.widget.insert(Tkinter.END, str(item))

    def getItems(self):
        return self.items

    def setSelection(self,selection):
        self.widget.select_clear(0,Tkinter.END)
        self.widget.select_set(selection)

    def getSelection(self):
        selection = self.widget.curselection()[0]
        try:
            selection = int(selection)
        except ValueError:
            pass
        return selection
    def _tk_clicked(self, event):
        send(self.proxy, 'select')

class RadioButtonWrapper(ComponentWrapper):

    groupMap = {}
    
    def __init__(self,*args,**kws):
        ComponentWrapper.__init__(self,*args,**kws)
        self._var = Tkinter.IntVar()
        self._var.set(0)

    def widgetFactory(self,*args,**kws):
        kws['command'] = self._tk_clicked
        kws['variable'] = self._var
        theWidge=Tkinter.Radiobutton(*args,**kws)
        return theWidge

    def setOn(self,on):
        if on:
            self.widget.select()
        else:
            self.widget.deselect()

    def getOn(self):
        return self._var.get() == int(self.widget.cget('value'))

    def setGroup(self,group):
        if group is None:
            self._var = Tkinter.IntVar()
            self.widget.configure(variable=self._var)
            return
        if self.proxy not in group._items:
            group._items.append(self.proxy)
        try:
            var = RadioButtonWrapper.groupMap[group]
        except KeyError:
            var = Tkinter.IntVar()
            RadioButtonWrapper.groupMap[group] = var
        self._var = var
        self.widget.configure(variable=self._var)

    def setValue(self,value):
        self.widget.configure(value=int(value))

    def getValue(self):
        return int(self.widget.cget('value'))

    def _tk_clicked(self,*args,**kws):
        send(self.proxy,'click')

class FrameWrapper(ComponentWrapper):

    def widgetFactory(self,*args,**kws):
        kws['relief'] = 'sunken'
        kws['borderwidth'] = 2
        theWidge=Tkinter.Frame(*args,**kws)
        return theWidge

    def setContainer(self,*args,**kws):
        """
        Ensure all contents are properly created. This looks like it could
        be handled at the Proxy level, but it probably *shouldn't* be -
        it's handling a Tk-specific requirement about the order in which
        widgets must be created. (I did it the Proxy way too. This way
        is definitely "the simplest thing that could possibly work.") - jak
        """
        ComponentWrapper.setContainer(self,*args,**kws)
        for component in self.proxy.contents:
            component.container = self.proxy

class WindowWrapper(ComponentWrapper):

    def __init__(self,proxy):
        ComponentWrapper.__init__(self,proxy)

    def internalProd(self):
        # Should check for None, but not properly implemented yet...
        try: self.proxy.container
        except AttributeError: return
        self.create()
        self.proxy.push()

    def closeHandler(self):
        self.destroy()
        application().remove(self.proxy)

    def resizeHandler(self, event):
        # FIXME: Shouldn't this simply set geometry, and have
        # setGeometry that call resized() or something? - mlh
        # No, we've already got new geometry, no need to
        # set it. - jak
        x,y,w,h = self.getGeometry()
        dw = w - self.proxy.width
        dh = h - self.proxy.height

        # Weird: why doesn't self.proxy.geometry give us the same values???
        oldGeo = self.proxy.x,self.proxy.y,self.proxy.width,self.proxy.height
        if (x,y,w,h) == oldGeo:
            # Do nothing unless we've actually changed size or position.
            # (Configure events happen for all kinds of wacky reasons,
            # most of which are already dealt with by Proxy code.) - jak
            return
        
        self.proxy.rawModify(width=w)
        self.proxy.rawModify(height=h)
        self.proxy.rawModify(x=x)
        self.proxy.rawModify(y=y)
        self.proxy.resized(dw, dh) # @@@ Implement this...

    def setUp(self):
        self.widget.protocol('WM_DELETE_WINDOW', self.closeHandler)
        self.widget.bind('<Configure>', self.resizeHandler)

    #def getGeometry(self):
    #    geo = self.widget.geometry()
    #    if not geo:
    #        return 100,100,10,10
    #    geo = geo.split('+')
    #    geo[0:1] = geo[0].split('x')
    #    w,h,x,y = map(int,geo)
    #    return x,y,w,h

    def getGeometry(self):
        g = self.widget.geometry()
        m = re.match('^(\d+)x(\d+)\+(\d+)\+(\d+)', g) # Hm...
        w = int(m.group(1))
        h = int(m.group(2))
        x = int(m.group(3))
        y = int(m.group(4))
        return x,y,w,h
    
    def setX(self, x):
        ox,y,w,h = self.getGeometry()
        self.setGeometry(x,y,w,h)

    def setY(self, y):
        x,oy,w,h = self.getGeometry()
        self.setGeometry(x,y,w,h)

    def setWidth(self, width):
        x,y,ow,h = self.getGeometry()
        self.setGeometry(x,y,width,h)

    def setHeight(self, height):
        x,y,w,oh = self.getGeometry()
        self.setGeometry(x,y,w,height)

    def setPosition(self, x, y):
        ox,oy,w,h = self.getGeometry()
        geometry = "%dx%d+%d+%d" % (w,h,x, y)
        self.widget.geometry(geometry)

    def setSize(self, width, height):
        x,y,ow,oh = self.getGeometry()
        geometry = "%dx%d+%d+%d" % (width, height,x,y)
        self.widget.geometry(geometry)        
    
    def setGeometry(self, x, y, width, height):
        geometry = "%dx%d+%d+%d" % (width, height, x, y)
        self.widget.geometry(geometry)
        self.widget.update()
    
    def setTitle(self, title):
        self.widget.title(title)

    def setContainer(self, container):
        # Ensure contents are properly created.
        for component in self.proxy.contents:
            component.container = self.proxy

    def setVisible(self, visible):
        if visible: self.widget.deiconify()
        else: self.widget.withdraw()

    def widgetFactory(self, *args, **kwds):
        return Tkinter.Toplevel(*args, **kwds)
