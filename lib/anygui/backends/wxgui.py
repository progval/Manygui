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
    
    def widgetFactory(self,*args,**kws):
        if hasattr(self.proxy.container,'wrapper'):
            parent = self.proxy.container.wrapper._wx_frame
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
'''COMMENT JKJKJK

class ListBox(ComponentMixin, AbstractListBox):
    _wx_class = wxListBox
    _wx_style = wxLB_SINGLE # FIXME: Not used... But default?

    def _backend_selection(self):
        if not self.noWidget():
            return self.widget.GetSelection()

    def _ensure_items(self):
        if not self.noWidget():
            for index in range(self.widget.Number()):
                self.widget.Delete(0)
            self.widget.InsertItems(map(str, list(self._items)), 0)

    def _ensure_selection(self):
        if not self.noWidget():
            if self.widget.Number() > 0:
                self.widget.SetSelection(int(self._selection)) # Does not cause an event

    def _ensure_events(self):
        if not self.noWidget():
            EVT_LISTBOX(self.widget, self._wx_id, self._wx_clicked)

    def _wx_clicked(self, event):
        send(self, 'select')

################################################################

class Button(ComponentMixin, AbstractButton):
    _wx_class = wxButton

    def _ensure_events(self):
        EVT_BUTTON(self.widget, self._wx_id, self._wx_clicked)

    def _wx_clicked(self, evt):
        send(self, 'click')

    def _get_wx_text(self):
        return str(self._text)


class ToggleButtonMixin(ComponentMixin):

    def _ensure_state(self):
        if self.widget is not None:
            self.widget.SetValue(int(self._on))

    def _get_wx_text(self):
        # return the text required for creation
        return str(self._text)


class CheckBox(ToggleButtonMixin, AbstractCheckBox):
    _wx_class = wxCheckBox

    def _wx_clicked(self, evt):
        val = self.widget.GetValue()
        if val == self._on:
            return
        self.modify(on=val)
        send(self, 'click')

    def _ensure_events(self):
        EVT_CHECKBOX(self.widget, self._wx_id, self._wx_clicked)

class RadioButton(ToggleButtonMixin, AbstractRadioButton):
    _wx_class = wxRadioButton

    def _wx_clicked(self, evt):
        if evt.GetInt():
            if self.group is not None:
                self.group.modify(value=self.value)
            send(self, 'click')
    
    def _ensure_created(self):
        # FIXME: What about moving buttons between groups? Would that
        # require destruction and recreation? [mlh20011214]
        # The first radiobutton in a group must have the wxRB_GROUP style
        if self._group and 0 == self._group._items.index(self):
            self._wx_style |= wxRB_GROUP
        return ToggleButtonMixin._ensure_created(self)

    def _ensure_events(self):
        EVT_RADIOBUTTON(self.widget, self._wx_id, self._wx_clicked)

################################################################

# IMPORTANT NOTE: Until the 'copy-paste' structure has been
# fixed (e.g. with a common superclass), fixes in one of these
# text classes should probably also be done in the other.

class TextField(ComponentMixin, AbstractTextField):
    _wx_class = wxTextCtrl

    def _backend_selection(self):
        if not self.noWidget():
            return self.widget.GetSelection()


    def _backend_text(self):
        if not self.noWidget():
            return  self.widget.GetValue()
            
    def _ensure_text(self):
        if not self.noWidget():
            # XXX Recursive updates seem to be no problem here,
            # wx does not seem to trigger the EVT_TEXT handler
            # when a new text equal to the old one is set.
            self.widget.SetValue(str(self._text))

    def _ensure_selection(self):
        if not self.noWidget():
            start, end = self._selection
            self.widget.SetSelection(int(start), int(end))

    def _ensure_editable(self):
        if not self.noWidget():
            self.widget.SetEditable(int(self._editable))

    def _ensure_events(self):
        EVT_TEXT_ENTER(self.widget, self._wx_id, self._wx_enterkey)
        EVT_KILL_FOCUS(self.widget, self._wx_killfocus)

    def _wx_killfocus(self, event):
        self.modify(text=self.widget.GetValue())

    def _wx_enterkey(self, event):
        send(self, 'enterkey')

    def _get_wx_text(self):
        # return the text required for creation
        # XXX From here or from model?
        return str(self._text)


# FIXME: 'Copy-Paste' inheritance... TA and TF could have a common wx
# superclass. The only differences are the _wx_style and event handling.
class TextArea(ComponentMixin, AbstractTextArea):
    _wx_class = wxTextCtrl
    _wx_style = wxTE_MULTILINE | wxHSCROLL

    def _backend_selection(self):
        if not self.noWidget():
            start, end = self.widget.GetSelection()
            if sys.platform[:3] == 'win':
                # under windows, the native widget contains
                # CRLF line separators
                # XXX Is this a wxPython bug?
                text = self.text
                start -= text[:start].count('\n')
                end -= text[:end].count('\n')
            return start, end

    def _backend_text(self):
        if not self.noWidget():
            return  self.widget.GetValue()
            
    def _ensure_text(self):
        if not self.noWidget():
            # XXX Recursive updates seem to be no problem here,
            # wx does not seem to trigger the EVT_TEXT handler
            # when a new text equal to the old one is set.
            self.widget.SetValue(str(self._text))

    def _ensure_selection(self):
        if not self.noWidget():
            start, end = self._selection
            if sys.platform[:3] == 'win':
                # under windows, the natice widget contains
                # CRLF line separators
                # XXX Is this a wxPython bug?
                text = self.text
                start += text[:start].count('\n')
                end += text[:end].count('\n')
            self.widget.SetSelection(int(start), int(end))

    def _ensure_editable(self):
        if not self.noWidget():
            self.widget.SetEditable(int(self._editable))

    def _ensure_events(self):
        EVT_KILL_FOCUS(self.widget, self._wx_killfocus)

    def _wx_killfocus(self, event):
        self.modify(text=self.widget.GetValue())

    def _get_wx_text(self):
        # return the text required for creation
        # XXX From here or from model?
        return str(self._text)

################################################################

class Frame(ComponentMixin, AbstractFrame):
    _wx_class = wxPanel

################################################################
END COMMENT JKJKJK '''

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

    # wxPython event handlers receive an event as parameter
    def _wx_close_handler(self, evt):
        self.destroy()

    def _wx_size_handler(self, evt):
        w, h = evt.GetSize()
        ow,oh = self._wx_frame.GetSize()
        self._wx_frame.SetSize((w, h))
        dw = w - ow
        dh = h - oh
        self.proxy.resized(dw, dh)

################################################################

class Application(AbstractApplication, wxApp):
    def __init__(self):
        AbstractApplication.__init__(self)
        wxApp.__init__(self, 0)
        
    def OnInit(self):
        return 1

    def internalRun(self):
        print "Entering wx mainloop"
        self.MainLoop()

################################################################
