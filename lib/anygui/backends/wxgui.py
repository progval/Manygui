from anygui.backends import *
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
        print "Resizing...",dw,dh
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
