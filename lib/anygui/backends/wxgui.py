from anygui.backends import *
import sys

#__all__ = anygui.__all__

__all__ = '''

  Application
  ButtonWrapper
  WindowWrapper
  LabelWrapper
  TextFieldWrapper
  TextAreaWrapper
  ListBoxWrapper
  FrameWrapper
  RadioButtonWrapper
  CheckBoxWrapper
  MenuBarWrapper
  MenuWrapper
  MenuCommandWrapper
  MenuCheckWrapper
  MenuSeparatorWrapper

'''.split()

ButtonWrapper=1
TextFieldWrapper=1
TextAreaWrapper=1
ListBoxWrapper=1
FrameWrapper=1
RadioButtonWrapper=1
CheckBoxWrapper=1

################################################################

from wxPython.wx import *
from anygui.Utils import log
from anygui.Applications import AbstractApplication
from anygui.Wrappers import AbstractWrapper, DummyWidget, isDummy
from anygui.Events import *
from anygui import application

from anygui.Windows import Window
from anygui.Menus import Menu, MenuCommand, MenuCheck, MenuSeparator

class ComponentWrapper(AbstractWrapper):
    # mixin class, implementing the backend methods

    _wx_id = None
    _wx_style = 0
    _needsCreationText = 1
    
    def __init__(self,*args,**kws):
        AbstractWrapper.__init__(self,*args,**kws)
        self.setConstraints('container','x','y','width','height',
                            'text','selection','geometry','visible')

    def widgetFactory(self,*args,**kws):
        if hasattr(self.proxy.container,'wrapper'):
            parent = self.proxy.container.wrapper._getContainer()
        else:
            parent = None
        if self._wx_id is None:
            self._wx_id = wxNewId()
        if self._needsCreationText:
            frame = self._wx_class(parent,
                                   self._wx_id,
                                   "NO SUCH WX TEXT",
                                   style=self._wx_style)
        else:
            frame = self._wx_class(parent,
                                   self._wx_id,
                                   style=self._wx_style)
        return frame

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

    def setGeometry(self,x,y,width,height):
        if self.noWidget(): return
        self.widget.SetPosition((int(x), int(y)))
        self.widget.SetSize((int(width), int(height)))

    def getGeometry(self):
        x,y = self.widget.GetPosition()
        w,h = self.widget.GetSize()
        return x,y,w,h

    # COMMON W/MSWGUI
    def setX(self,x):
        if self.noWidget(): return
        ox,y,w,h = self.getGeometry()
        self.setGeometry(x,y,w,h)

    def setY(self,y):
        if self.noWidget(): return
        x,oy,w,h = self.getGeometry()
        self.setGeometry(x,y,w,h)

    def setWidth(self,width):
        if self.noWidget(): return
        x,y,ow,h = self.getGeometry()
        self.setGeometry(x,y,width,h)

    def setHeight(self,height):
        if self.noWidget(): return
        x,y,w,oh = self.getGeometry()
        self.setGeometry(x,y,w,height)
    # END COMMON W/MSWGUI

    def setSize(self,width,height):
        if self.noWidget(): return
        self.widget.SetSize(width,height)

    def setPosition(self,x,y):
        if self.noWidget(): return
        self.widget.SetPosition(x,y)

    def setVisible(self,visible):
        if not self.noWidget():
            self.widget.Show(int(visible))

    def setEnabled(self,enabled):
        if not self.noWidget():
            self.widget.Enable(int(enabled))

    def destroy(self):
        if not self.noWidget():
            self.widget.Destroy()
            self.widget = DummyWidget()
        try:
            self._forgetContents()
        except AttributeError:
            pass

    def setText(self,text):
        if not self.noWidget() and hasattr(self.widget, 'SetLabel'):
            self.widget.SetLabel(str(text))

    def getText(self):
        if not self.noWidget() and hasattr(self.widget, 'SetLabel'):
            return self.widget.GetLabel()
        return ""

    def enterMainLoop(self):
        self.proxy.push()

################################################################

class LabelWrapper(ComponentWrapper):
    _wx_class = wxStaticText
    _wx_style = wxALIGN_LEFT

################################################################

class ButtonWrapper(ComponentWrapper):
    _wx_class = wxButton

    def widgetSetUp(self):
        EVT_BUTTON(self.widget, self._wx_id, self._wx_clicked)

    def _wx_clicked(self, evt):
        send(self.proxy, 'click')

################################################################

class ListBoxWrapper(ComponentWrapper):
    _wx_class = wxListBox
    _wx_style = wxLB_SINGLE # FIXME: Not used... But default?
    _needsCreationText=0

    def getSelection(self):
        if not self.noWidget():
            return self.widget.GetSelection()

    def setItems(self,items):
        if not self.noWidget():
            for index in range(self.widget.Number()):
                self.widget.Delete(0)
            self.widget.InsertItems(map(str, list(items)), 0)

    def setSelection(self,selection):
        if not self.noWidget():
            if self.widget.Number() > 0:
                self.widget.SetSelection(int(selection)) # Does not cause an event

    def widgetSetUp(self):
        if not self.noWidget():
            EVT_LISTBOX(self.widget, self._wx_id, self._wx_clicked)

    def _wx_clicked(self, event):
        send(self.proxy, 'select')

################################################################

class ToggleButtonWrapper(ComponentWrapper):

    def setOn(self,on):
        if not self.noWidget():
            self.widget.SetValue(int(on))

    def getOn(self):
        if not self.noWidget():
            return self.widget.GetValue()

class CheckBoxWrapper(ToggleButtonWrapper):
    _wx_class = wxCheckBox

    def widgetSetUp(self):
        EVT_CHECKBOX(self.widget, self._wx_id, self._wx_clicked)

    def _wx_clicked(self, evt):
        send(self.proxy, 'click')


class RadioButtonWrapper(ToggleButtonWrapper):
    _wx_class = wxRadioButton

    def _wx_clicked(self, evt):
        if self.getOn():
            send(self.proxy, 'click')
    
    def widgetFactory(self,*args,**kws):
        # FIXME: What about moving buttons between groups? Would that
        # require destruction and recreation? [mlh20011214]
        # The first radiobutton in a group must have the wxRB_GROUP style
        if self.proxy.group and self.proxy.group._items.index(self.proxy) == 0:
            self._wx_style |= wxRB_GROUP
        return ToggleButtonWrapper.widgetFactory(self,*args,**kws)

    # COMMON WITH MSW
    def setGroup(self,group):
        if group is None:
            return
        if self.proxy not in group._items:
            group._items.append(self.proxy)
    # END COMMON WITH MSW

    def widgetSetUp(self):
        EVT_RADIOBUTTON(self.widget, self._wx_id, self._wx_clicked)

################################################################

################################################################

# IMPORTANT NOTE: Until the 'copy-paste' structure has been
# fixed (e.g. with a common superclass), fixes in one of these
# text classes should probably also be done in the other.

class TextControlMixin:

    def getText(self):
        if not self.noWidget():
            if sys.platform[:3] == 'win':
                return self.widget.GetValue().replace('\r','')
            else:
                return self.widget.GetValue()
            
    def setText(self,text):
        if not self.noWidget():
            # XXX Recursive updates seem to be no problem here,
            # wx does not seem to trigger the EVT_TEXT handler
            # when a new text equal to the old one is set.
            self.widget.SetValue(str(text))

    def setEditable(self,editable):
        if not self.noWidget():
            self.widget.SetEditable(int(editable))

class TextFieldWrapper(TextControlMixin,ComponentWrapper):
    _wx_class = wxTextCtrl

    def getSelection(self):
        if not self.noWidget():
            return self.widget.GetSelection()

    def setSelection(self,selection):
        if not self.noWidget():
            start, end = selection
            self.widget.SetSelection(int(start), int(end))

    def widgetSetUp(self):
        EVT_TEXT_ENTER(self.widget, self._wx_id, self._wx_enterkey)

    def _wx_enterkey(self, event):
        send(self.proxy, 'enterkey')

class TextAreaWrapper(TextControlMixin,ComponentWrapper,TextControlMixin):
    _wx_class = wxTextCtrl
    _wx_style = wxTE_MULTILINE | wxHSCROLL

    def getSelection(self):
        if not self.noWidget():
            start, end = self.widget.GetSelection()
            if sys.platform[:3] == 'win':
                # under windows, the native widget contains
                # CRLF line separators
                # XXX Is this a wxPython bug?
                # (Probably not, one wants to be able to cut&paste
                # normally under windows. It would be nice if
                # the selection was returned in a saner manner,
                # however.)

                # I -think- this is right, now. We need to find the
                # number of newlines spanned by the selection in
                # the non-Windowfied text in order to do this
                # properly. If anyone notices a problem with
                # wx TextArea selections, please fix it :-) - jak
                
                span = end-start
                text = self.widget.GetValue()
                unxText = text.replace('\r','')
                startCt = text[:start].count('\n')
                unxStart = start-startCt
                spanBreaks = unxText[unxStart:(unxStart+span)].count('\n')
                endCt = startCt+spanBreaks
                start -= startCt
                end -= endCt
            return start, end

    def setSelection(self,selection):
        if not self.noWidget():
            start, end = selection
            if sys.platform[:3] == 'win':
                # under windows, the natice widget contains
                # CRLF line separators
                # XXX Is this a wxPython bug?
                text = self.getText()
                start += text[:start].count('\n')
                end += text[:end].count('\n')
            self.widget.SetSelection(int(start), int(end))

################################################################

class FrameWrapper(ComponentWrapper):
    _wx_class = wxPanel
    _needsCreationText = 0

    def _getContainer(self): return self.widget

    def _forgetContents(self):
        # Special code to blow away contents when a frame is destroyed.
        # This is necessary because wx widgets are apparently implicitly
        # destroyed when their container is, and if we try to call
        # ComponentWrapper.destroy() on a widget that's been destroyed
        # in this way, we crash and burn (on Windows anyway).
        for comp in self.proxy.contents:
            try:
                comp.wrapper._forgetContents()
            except AttributeError:
                pass
            comp.wrapper.widget = DummyWidget()

    def setContainer(self, *args, **kws):
        """
        OK, this probably needs to be pulled into a mixin heritable by
        various backends.
        
        Ensure all contents are properly created. This looks like it could
        be handled at the Proxy level, but it probably *shouldn't* be -
        it's handling a Tk-specific requirement about the order in which
        widgets must be created. (I did it the Proxy way too. This way
        is definitely "the simplest thing that could possibly work.") - jak
        """
        ComponentWrapper.setContainer(self, *args, **kws)
        for component in self.proxy.contents:
            component.container = self.proxy

################################################################

class WindowWrapper(ComponentWrapper):
    _wx_class = wxFrame
    _wx_style = wxDEFAULT_FRAME_STYLE | wxNO_FULL_REPAINT_ON_RESIZE
    _wx_frame = None

    def setGeometry(self,x,y,width,height):
        # override this to set the CLIENT size (not the window size)
        # to take account for title bar, borders and so on.
        if not self.noWidget():
            self.widget.SetPosition((int(x), int(y)))
            self.widget.SetClientSize((int(width), int(height)))

    def getGeometry(self):
        x,y = self.widget.GetPosition()
        w,h = self.widget.GetClientSize()
        return x,y,w,h
        
    def widgetFactory(self,*args,**kws):
        result = ComponentWrapper.widgetFactory(self,*args,**kws)
        if result:
            # Controls should be contained in a wxPanel (which
            # is itself contained in the wxFrame)
            # Using the default style gives us proper handling
            # of TAB to move between the controls.
            self._wx_frame = wxPanel(result, wxNewId())
            self._wx_frame.SetSize((1,1))
        return result
    
    def widgetSetUp(self):
        EVT_CLOSE(self.widget, self._wx_close_handler)
        EVT_SIZE(self.widget, self._wx_size_handler)

    def setTitle(self,title):
        if not self.noWidget():
            self.widget.SetTitle(str(title))

    def setContainer(self,container):
        if not application().isRunning(): return
        if container is None: return
        if self.noWidget():
            self.create()
        self.proxy.push(blocked=['container'])
        # Ensure contents are properly created.
        for comp in self.proxy.contents:
            comp.container = self.proxy

    def _getContainer(self): return self._wx_frame

    # wxPython event handlers receive an event as parameter
    def _wx_close_handler(self, evt):
        self.destroy()

    def _wx_size_handler(self, evt):
        #w, h = evt.GetSize()
        w,h = self.widget.GetClientSize()
        ow,oh = self._wx_frame.GetSize()
        self._wx_frame.SetSize((w, h))
        if (ow,oh) == (1,1):
            return
        dw = w - ow
        dh = h - oh
        if (dw,dh) == (0,0):
            return
        self.proxy.resized(dw,dh)

################################################################

class Application(AbstractApplication, wxApp):
    def __init__(self):
        AbstractApplication.__init__(self)
        wxApp.__init__(self, 0)
        
    def OnInit(self):
        return 1

    def internalRun(self):
        self.MainLoop()

################################################################
# Menus

class WxMenuDummy:
    # No native widget for menu items, but we still need to provide
    # -something- for create() to chew on.
    pass

class MenuItemMixin:

    def widgetFactory(self,*args,**kws):
        return WxMenuDummy()

    _idSrc = 0
    def getId(self):
        MenuItemMixin._idSrc = MenuItemMixin._idSrc + 1
        return MenuItemMixin._idSrc

    def createIfNeeded(self):
        if self.noWidget():
            self.create()
            self._id = self.getId()

    def setEnabled(self,enabled):
        #print "setEnabled",self,enabled
        if self.proxy.container is None or self.proxy.container.wrapper.noWidget():
            return
        self.rebuild_all()

    def setContainer(self,container):
        #print "MenuItemMixin.setContainer",self,container
        if not container:
            if self.proxy.container is None:
                return
            if self.proxy in self.proxy.container.contents:
                self.proxy.container.contents.remove(self.proxy)
            self.widget = DummyWidget()
            self.proxy.container.wrapper.rebuild()
        else:
            self.createIfNeeded()
            self.proxy.container.wrapper.rebuild()

    def setText(self,text):
        if self.proxy.container is None or self.proxy.container.wrapper.noWidget():
            return
        try:
            self.rebuild_all()
        except:
            pass

    def enterMainLoop(self): # ...
        pass

    def internalDestroy(self):
        pass

    def __str__(self):
        if self.noWidget():
            widg = "NOWIDGET"
        else:
            widg = self.widget
        return "%s %s@%s w%s"%(self.__class__.__name__.split('.')[-1],self.proxy.state.get('text','NONE'),id(self),widg)

class MenuBarWrapper(MenuItemMixin,AbstractWrapper):

    def __init__(self,*args,**kws):
        AbstractWrapper.__init__(self,*args,**kws)
        self.full = 0

    def widgetFactory(self,*args,**kws):
        return wxMenuBar(*args,**kws)

    def setContainer(self,container):
        if not container:
            if self.noWidget:
                return
            #print "DESTROYING",self
            #self.widget.destroy()
            self.widget = DummyWidget()
        else:
            if container.wrapper.noWidget():
                return
            #print "Adding menubar",self,"to",self.proxy.container.wrapper
            self.createIfNeeded()
            container.wrapper.widget.SetMenuBar(self.widget)
            self.full = 0
            self.rebuild()

    def setContents(self,contents):
        self.rebuild()

    def rebuild_all(self):
        self.rebuild()

    def rebuild(self):
        #print "REBUILDING",self
        if self.proxy.container is None:
            return
        if self.proxy.container.wrapper.noWidget():
            return

        self.removeAll()

        self.full = 1

        pos = 0
        for item in self.proxy.contents:
            item.wrapper.widget = DummyWidget()
            item.wrapper.rebuild()
            #print "\tAdding",item.wrapper
            self.widget.Append(item.wrapper.widget,item.text)
            if not item.enabled:
               self.widget.Enable(pos,0)
            pos = pos+1

    def removeAll(self):
        if self.full:
            for item in range(len(self.proxy.contents)):
                self.widget.Remove(0)

    def enterMainLoop(self): # ...
        self.proxy.push() # FIXME: Why is this needed when push is called in internalProd (by prod)?

class MenuWrapper(MenuItemMixin,AbstractWrapper):

    def __init__(self,*args,**kws):
        AbstractWrapper.__init__(self,*args,**kws)
        self.full = 0

    def widgetFactory(self,*args,**kws):
        return wxMenu(*args,**kws)

    def setContainer(self,container):
        if not container:
            if self.noWidget:
                return
            #if self.proxy in self.proxy.container.contents:
            #    self.proxy.container.contents.remove(self.proxy)
            #print "DESTROYING",self
            #self.widget.destroy()
            self.widget = DummyWidget()
            self.proxy.container.wrapper.rebuild()
        else:
            if container.wrapper.noWidget():
                return
            self.full = 0
            self.rebuild()

    def setContents(self,contents):
        self.rebuild_all()

    def rebuild_all(self):
        """
        Rebuild the entire menu structure starting from the toplevel menu.
        """
        if self.proxy.container is None:
            return
        if self.noWidget():
            return
        if self.proxy.container.wrapper.noWidget():
            return
        proxies = [self.proxy]
        while not isinstance(proxies[-1],Window):
            proxies.append(proxies[-1].container)
        proxies[-2].wrapper.rebuild()

    def rebuild(self):
        """
        Rebuild the menu structure of self and all children; re-add
        self to parent.
        """
        if self.proxy.container is None:
            return
        if self.proxy.container.wrapper.noWidget():
            return

        #print "\tREBUILDING",self,self.proxy.contents
        if not self.noWidget() and self.full:
            #print "\t\tDELETING CONTENTS OF",self.widget
            ids = [p.wrapper._id for p in self.proxy.contents]
            for id in ids:
                try:
                    #print '\t\t\tTRYING To DELETE',id
                    self.widget.Delete(id)
                    #print "\t\t\tDeleted",id
                except:
                    #print "\t\t\tEXCEPTION while deleting",id,sys.exc_info()
                    pass
        #print "\t\tCREATING WIDGET"
        self.createIfNeeded()
        #print "\t\t\tDONE",self.widget

        self.full = 1

        for item in self.proxy.contents:
            if isinstance(item,Menu):
                item.wrapper.widget = DummyWidget()
                item.wrapper.rebuild()
                #print "\t\t\tADDING",item.wrapper,item.wrapper._id
                self.widget.AppendMenu(item.wrapper._id,item.text,item.wrapper.widget)
                if not item.enabled:
                    self.widget.Enable(item.wrapper._id,0)
                continue
            item.wrapper.createIfNeeded()
            #print "\t\t\tADDING",item.wrapper,item.wrapper._id
            if isinstance(item,MenuCommand):
                self.widget.Append(item.wrapper._id,item.text,"",0)
                EVT_MENU(self.widget,item.wrapper._id,item.wrapper.clickHandler)
                if not item.enabled:
                    self.widget.Enable(item.wrapper._id,0)
            if isinstance(item,MenuCheck):
                self.widget.Append(item.wrapper._id,item.text,"",1)
                EVT_MENU(self.widget,item.wrapper._id,item.wrapper.clickHandler)
                if not item.enabled:
                    self.widget.Enable(item.wrapper._id,0)
                try:
                    on = item.state['on']
                except KeyError:
                    on=0
                self.widget.Check(item.wrapper._id,on)
            if isinstance(item,MenuSeparator):
                self.widget.AppendSeparator()
                #print "Adding separator",item.wrapper,"to",self
                pass

    def enterMainLoop(self): # ...
        self.proxy.push() # FIXME: Why is this needed when push is called in internalProd (by prod)?

class MenuCommandWrapper(MenuItemMixin,AbstractWrapper):

    def __init__(self,*args,**kws):
        AbstractWrapper.__init__(self,*args,**kws)

    def clickHandler(self,*args,**kws):
        #print "CLICKED",self
        send(self.proxy,'click',text=self.proxy.text)

class MenuCheckWrapper(MenuCommandWrapper):

    def __init__(self,*args,**kws):
        MenuCommandWrapper.__init__(self,*args,**kws)
        # FIX ME! self.var = Tkinter.IntVar()

    def setOn(self,on):
        if self.noWidget():
            return
        #print "setOn",self.proxy,self.proxy.container
        #print "MenuCheck.setOn",self,on
        # FIX ME! self.var.set(on)
        self.proxy.container.wrapper.widget.Check(self._id,on)

    def getOn(self):
        if self.noWidget():
            return
        #print "getOn",self.proxy,self.proxy.container
        #print "MenuCheck.getOn",self,self.var.get()
        # FIX ME! return self.var.get()
        return self.proxy.container.wrapper.widget.IsChecked(self._id)

class MenuSeparatorWrapper(MenuItemMixin,AbstractWrapper):
    pass

################################################################
