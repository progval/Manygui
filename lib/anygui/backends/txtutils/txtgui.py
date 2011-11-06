"""txtgui.py is the curses/text binding for Anygui <http://www.anygui.org>.
"""
import anygui.backends.txtutils.txtwgts as tw

import sys
sys.stderr = open('error.txt','w')
import os

from anygui.backends import *
from anygui.Applications import AbstractApplication
from anygui.Wrappers import AbstractWrapper, DummyWidget, isDummy
from anygui.Events import *
from anygui.Exceptions import Error
from anygui.Utils import log,setLogFile
from anygui import application

setLogFile("txtgui.log")

def setScreenPackage(pkg):
    if pkg == "curses":
        from . import scr_curses
        tw._scr = scr_curses
    else:
        from . import scr_text
        tw._scr = scr_text
    setScale()

def setScale():
    x,y = tw._scr._xsize,tw._scr._ysize
    tw.set_scale(x,y)

class ComponentWrapper(AbstractWrapper):

    def __init__(self, *args, **kwds):
        AbstractWrapper.__init__(self, *args, **kwds)

        # 'container' before everything...
        self.setConstraints('container','x','y','width','height','text','selection')
        # Note: x,y,width, and height probably have no effect here, due to
        # the way getSetters() works. I'm not sure if that's something
        # that needs fixing or not... - jak
        
        self.addConstraint('geometry', 'visible')
        # FIXME: Is this the right place to put it? Make sure
        # 'geometry' implies 'x', 'y', etc. too (see Wrappers.py)
        # Also, this scheme will cause flashing... (place before
        # place_forget)

    def widgetFactory(self,*args,**kws):
        return self._twclass(*args,**kws)

    def setGeometry(self,x,y,width,height):
        ##_scr.dbg("Ensuring geometry",self.geometry,self)
        #_refresh_all()
        if self.noWidget(): return
        self.widget.set_geometry((x,y,width,height))

    def setVisible(self,visible):
        if self.noWidget(): return
        self.widget.set_visible(visible)

    def getVisible(self):
        if self.noWidget(): return
        return self.widget.is_visible()

    def setEnabled(self,enabled):
        #_scr.dbg("ENSURING ENABLED",self)
        # UNTESTED!
        if self.noWidget(): return
        self.widget.set_enabled(enabled)

    def destroy(self):
        if self.noWidget(): return
        self.widget.destroy()
        self.widget.set_parent(None)
        self.widget = DummyWidget()

    def setText(self,text):
        if self.noWidget(): return
        self.widget.set_text(text)

    def enterMainLoop(self): # ...
        #if not isDummy(self.widget):
        #    self.widget.destroy()
        #    sys.stdout.flush()
        self.proxy.push() # FIXME: Why is this needed when push is called in internalProd (by prod)?

    def setContainer(self,container):
        #log("Set container",self,container)
        if not self.noWidget():
            self.destroy()
        if container is None:
            self.widget.parent = None
            return
        self.create()
        container.wrapper.widget.add(self.widget)
        self.widget.create()
        self.proxy.push(blocked=['container'])

class LabelWrapper(ComponentWrapper):
    _twclass = tw.Label

class ListBoxWrapper(ComponentWrapper):
    _twclass = tw.ListBox

    def setItems(self,items):
        if self.noWidget(): return
        self.widget.set_items(items)

    def getItems(self):
        if self.noWidget(): return
        return self.widget.items

    def setSelection(self,selection):
        if self.noWidget(): return
        self.widget.set_selection(selection)

    def getSelection(self):
        if self.noWidget(): return
        return self.widget.get_selection()

    def widgetSetUp(self):
        self.widget.command = self._twClick

    def _twClick(self,lb,sel,sel_item):
        log("Got click",sel,sel_item)
        send(self.proxy,'select')

#class CanvasWrapper(ComponentWrapper):
#    _twclass = tw.Canvas

class ButtonMixin:

    def widgetSetUp(self):
        self.widget.command = self._twClick

    def _twClick(self,btn=None,*args,**kws):
        send(self.proxy,'click')

class ButtonWrapper(ButtonMixin,ComponentWrapper):
    _twclass = tw.Button

class ToggleButtonMixin(ButtonMixin):

    def getOn(self):
        if self.noWidget(): return
        log(self,"getOn",self.widget.get_state())
        return self.widget.get_state()

    def setOn(self,on):
        if self.noWidget(): return
        self.widget.set_state(on)

class CheckBoxWrapper(ToggleButtonMixin,ComponentWrapper):
    _twclass = tw.CheckBox

class RadioButtonWrapper(ToggleButtonMixin,ComponentWrapper):
    _twclass = tw.RadioButton

    def setGroup(self,group):
        if group == None:
            return
        if self.proxy not in group._items:
            group._items.append(self.proxy)

    def _twClick(self,btn=None,*args,**kws):
        try:
            self.proxy.group.value = self.proxy.value
        except AttributeError:
            pass
        ToggleButtonMixin._twClick(self,btn,*args,**kws)

class TextControlMixin:

    def getText(self):
        if not self.noWidget():
            return self.widget.get_text()
            
    def setText(self,text):
        if not self.noWidget():
            self.widget.set_text(str(text))

    def setEditable(self,editable):
        if not self.noWidget():
            self.widget.set_editable(int(editable))

    def getSelection(self):
        if not self.noWidget():
            return self.widget.get_selection()

    def setSelection(self,selection):
        if not self.noWidget():
            self.widget.set_selection(selection)

class TextFieldWrapper(TextControlMixin,ComponentWrapper):
    _twclass = tw.TextField

    def widgetSetup(self):
        self.widget.focus_lost_cmd = self.handleEnterKey

    def handleEnterKey(self,*args,**kws):
        send(self.proxy, 'enterkey')

class TextAreaWrapper(TextControlMixin,ComponentWrapper):
    _twclass = tw.TextArea

class ContainerMixin:

    def resize(self,dw,dh):
        self.proxy.resized(dw, dh)

    def setContainer(self,container):
        if not self.noWidget():
            self.destroy()
        if container is None:
            self.widget.parent = None
            return
        #if container.wrapper.noWidget(): return
        self.create()
        self.addToContainer(container)
        self.widget.create()
        self.proxy.push(blocked=['container'])
        for comp in self.proxy.contents:
            comp.container = self.proxy

class FrameWrapper(ContainerMixin,ComponentWrapper):
    _twclass = tw.Frame

    def __init__(self,*args,**kws):
        ComponentWrapper.__init__(self,*args,**kws)

    def addToContainer(self,container):
        container.wrapper.widget.add(self.widget)

class WindowWrapper(ContainerMixin,ComponentWrapper):
    """To move or resize a window, use Esc-W to open
the window menu, then type h,j,k, or l to move, and
H,J,K, or L to resize."""

    _twclass = tw.Window

    def __init__(self,*args,**kws):
        ComponentWrapper.__init__(self,*args,**kws)

    def setTitle(self,title):
        if self.noWidget(): return
        self.widget.set_title(title)

    def addToContainer(self,container):
        application().txtapp.add(self.widget)
        self.widget.resize_command = self.resize

class Application(AbstractApplication):

    def __init__(self):
        AbstractApplication.__init__(self)
        self.txtapp = tw.Application()

    def internalRun(self):
        self.txtapp.run()
