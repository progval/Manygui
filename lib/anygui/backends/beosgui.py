
from anygui.backends import *
__all__ = anygui.__all__

#################################################################

# All Bethon modules are imported.  Not all are used.

import BAlert, BApplication
import BButton
import BCheckBox, BControl
import BFile, BFilePanel, BFont
import BListItem, BListView
import BMenuBar, BMenuItem, BMenu, BMessage
import BOutlineListView
import BPath, BPopUpMenu
import BRadioButton
import BScrollBar, BScrollView, BSeparatorItem, BSlider, BStatusBar, BStringItem, BStringView
import BTab, BTabView, BTextControl, BTextView
import BView, BVolume
import BWindow

"""

Not used list...:-)

 BControl, BFile, BFilePanel, BFont, BListItem,
 BMenuBar, BMenuItem, BMenu, BOutlineListView, BPath,
 BPopUpMenu, BScrollBar, BSeparatorItem, BSlider,
 BStatusBar, BTab, BTabView, BView, BVolume
 
"""
# BeOS constants B_<stuff>

from AppKit import *
from SupportKit import *
from InterfaceKit import *
from StorageKit import *

ACTION = 6666 # BMessage value
               
#################################################################

class WrapThis:
    """Binds instance with BeOS API object.  Objects
that support this operation can call Python bound methods from
their virtual function ``hooks'', so things like MessageReceived()
work in Python.  Stolen blatantly from Donn."""

    def wrap(self, this):
        self._beos_comp = this
        self._beos_comp.bind(self)

    def sub_wrap(self, this):
        # For widgets with scrollbox surrounding them.
        self._beos_sub = this
        self._beos_sub.bind(self)

#################################################################

class ComponentMixin(WrapThis):
    "Base class for all components."
        
    _beos_comp = None
    _beos_sub = None
    _beos_id = 0
    _beos_style = None
    _beos_msg = None
    _beos_clicked = None
    _lost_focus = None
    _beos_mode = B_FOLLOW_LEFT + B_FOLLOW_TOP
    _beos_flags = B_WILL_DRAW + B_NAVIGABLE

    _init_args = None
    	
    def _ensure_created(self):
        if not self._is_created():
            self._beos_id = str(self._beos_id)
            self._ensure_visibility()
            self._ensure_events()
            self._ensure_geometry()
            if self._init_args is None:
                self._init_args = (self._beos_bounds,
                                   str(self._beos_id),
                                   self._text,
                                   self._beos_msg,
                                   self._beos_mode,
                                   self._beos_flags)
            self.wrap(self._beos_class(*self._init_args))
            self._ensure_geometry()
            #print self._beos_class, self._beos_id
            self._ensure_enabled_state()
            if self._container is not None:
                self._container._ensure_created()
                self._container._beos_comp.AddChild(self._beos_comp)
            ComponentMixin._beos_id += 1 # Gives each component a unique id
            self._finish_creation()
            return 1
        return 0
    
    def _ensure_destroyed(self):
        if self._beos_comp:
            if self._container:
                self._container._beos_remove(self)
            self._beos_comp = None
        
    def _is_created(self):
        return self._beos_comp is not None
    
    def _ensure_events(self):
        #if self._action:
        #    print self._action
        self._beos_msg = BMessage.BMessage(ACTION)              # Create a BMessage instance
        self._beos_msg.AddString('self_id', str(self._beos_id)) # Add the id of the object
    
    def _ensure_geometry(self):
        self._beos_bounds = (float(self._x),
                float(self._y),
                float(self._width+ self._x),
                float(self._height+self._y))

    def _ensure_visibility(self):
        if self._beos_comp:
            if self._visible:
                if self._beos_comp.IsHidden():
                    self._beos_comp.Show()
            else:
                if self._beos_comp.IsHidden():
                    pass # Don't Hide stuff twice...
                else:
                    self._beos_comp.Hide()
        
    def _ensure_enabled_state(self):
        pass

    def _get_beos_text(self):
        # helper function for creation
        # returns the text required for creation.
        # This may be the _text property, or _title, ...,
        # depending on the subclass
        return self._text

    def _ensure_text(self):
        pass

#################################################################

class Label(ComponentMixin, AbstractLabel):
    """Designed for single lines of text only."""
    _beos_class = BStringView.BStringView
    _beos_flags = B_WILL_DRAW
    _text = "BStringItem"
    
    def _ensure_created(self):
        self._ensure_geometry()
        self._beos_id = str(self._beos_id)
        self._init_args = (self._beos_bounds,
                           self._beos_id,
                           self._text,
                           self._beos_mode,
                           self._beos_flags)
        result = ComponentMixin._ensure_created(self)
        self._ensure_text()
        return result
    
    def _ensure_text(self):
        if self._beos_comp:
            pass
            #self._beos_comp.LockLooper()
            self._beos_comp.SetText(str(self._text))
            #self._beos_comp.UnlockLooper()
            self._ensure_geometry()
            #self._beos_comp.ResizeToPreferred()
    
    def _ensure_events(self):
        pass

##################################################################

class ListBox(ComponentMixin, AbstractListBox):
    _beos_sub_class = BListView.BListView
    _beos_type = B_SINGLE_SELECTION_LIST
    _beos_mode = B_WILL_DRAW + B_NAVIGABLE + B_FRAME_EVENTS #+ B_FOLLOW_ALL_SIDES #??
    _beos_class = BScrollView.BScrollView
    _beos_flags = 0
    _horizontal = 0
    _vertical = 1
    _beos_border = B_FANCY_BORDER
    
    def _ensure_created(self):
        self._beos_id = str(self._beos_id)
        self._ensure_geometry()
        if self._beos_sub is None:
            self.sub_wrap(self._beos_sub_class(self._beos_bounds,
                                         self._beos_id,
                                         self._beos_type,
                                         self._beos_mode,
                                         self._beos_flags))
            self._init_args = (self._beos_id,
                           self._beos_sub,
                           self._beos_mode,
                           self._beos_flags,
                           self._horizontal,
                           self._vertical,
                           self._beos_border)
            result = ComponentMixin._ensure_created(self)
            self._ensure_items()
            self._ensure_selection()
            self._ensure_events()
            return result
    
    def _ensure_geometry(self):
        self._beos_bounds = (float(self._x),
                float(self._y),
                float(self._width+ self._x-15),
                float(self._height+self._y))
        
    def _backend_selection(self):
        if self._beos_comp:
            return self._beos_sub.CurrentSelection()
            
    def _ensure_items(self):
        if self._beos_comp:
            self._beos_sub.MakeEmpty()
            for item in self._items:
                self._beos_sub.AddItem(BStringItem.BStringItem(str(item)))
    
    def _ensure_selection(self):
        return # Select() crashes.
        if self._beos_comp:
            self._beos_sub.Select(self._selection)
    
    #def _ensure_events(self):
    #    "For double-click."
    #    if self._beos_comp:
    #        ComponentMixin._ensure_events(self)
    #        self._beos_sub.SetInvocationMessage(self._beos_msg)

    # BeOS hook function
    def SelectionChanged(self):
        """Might be replaced by InvocationMessage."""
        send(self, 'select')
    
            
###################################################################

class Button(ComponentMixin, AbstractButton):
    _beos_class = BButton.BButton
    
    def _ensure_text(self):
        if self._beos_comp:
    	    self._beos_comp.SetLabel(str(self._text))

    def _ensure_enabled_state(self):
        if self._beos_comp:
            self._beos_comp.SetEnabled(self._enabled)
    
    def _beos_clicked(self):
        send(self, 'click')


class ToggleButtonMixin(ComponentMixin):

    def _ensure_state(self):
        if self._beos_comp is not None:
            self._beos_comp.SetValue(self.on)

    def _ensure_enabled_state(self):
        if self._beos_comp:
            self._beos_comp.SetEnabled(self._enabled)
            
    def _get_on(self):
        return self._beos_comp.Value()
    
       
    def _beos_clicked(self):
        val = self._get_on()
        send(self, 'click')
        if val == self._on:
            return
        self.modify(on=val)
        

     
class CheckBox(ToggleButtonMixin, AbstractCheckBox):
    _beos_class = BCheckBox.BCheckBox


class RadioButton(ToggleButtonMixin, AbstractRadioButton):
    _beos_class = BRadioButton.BRadioButton
    
    def _beos_clicked(self):
        if self.group is not None:
            self.group.modify(value=self.value)
        send(self, 'click')


class RadioGroup(RadioGroup):
    _beos_class = BView.BView 
    """ FIXME: forces all buttons into the one group.
               Selecting a button from another group
               has the same effect as choosing the button 
               in that position in the first group.
    """
    def _get_value(self):
        value = 0
        for item in self._items:
            if item._beos_class == BRadioButton.BRadioButton:
                if item._beos_comp.Value() == B_CONTROL_ON:
                    return value
            value += 1
    
    def add(self, buttons):
        for btn in buttons:
            btn.group = self
    
'''
class RadioGroup(ComponentMixin, Attrib, Action):
    """Needs lots of work."""
    _beos_class = BView.BView
    _beos_bounds = (0.0,0.0,260.0,150.0)
    _items = None
    _value = None
    _container = None

    def __init__(self, items=[], **kw):
        Attrib.__init__(self, **kw)
        self.modify(_items=[])
        self.add(items)

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        if self._value != value:
            self.modify(_value=value)
            for item in self._items:
                item._update_state()
            self._beos_clicked()

    def add(self, buttons):
        if buttons and (self._beos_comp is None):
            self._ensure_created()
        for btn in buttons:
            btn.group = self
            if btn._beos_comp is None:
                btn._ensure_created()
            self._beos_comp.AddChild(btn._beos_comp)
            #self._beos_comp.ResizeToPreferred()

    def remove(self, buttons):
        for btn in buttons:
            if btn in self._items:
                btn.group = None
        
    def _ensure_created(self):
        self._beos_id = str(self._beos_id)
        #print application()
        self._init_args = (self._beos_bounds,
                           self._beos_id,
                           self._beos_mode,
                           self._beos_flags)
        return ComponentMixin._ensure_created(self)
        
 '''           
#################################################################

#class TextComponentMixin(ComponentMixin, AbstractTextComponent):
#    _text = ''
    
class TextField(ComponentMixin, AbstractTextField):
    _beos_class = BTextControl.BTextControl
    _label = None 
    
    def _ensure_created(self):
        self._beos_id = str(self._beos_id)
        self._ensure_events()
        self._ensure_geometry()
        self._init_args = (self._beos_bounds,
                           self._beos_id,
                           self._label, # !!!
                           self._text,
                           self._beos_msg,
                           self._beos_mode,
                           self._beos_flags)
        result = ComponentMixin._ensure_created(self)
        self._ensure_editable()
        self._ensure_enabled_state()
        self._ensure_text()
        return result
    
    def _backend_text(self):
        if self._beos_comp:
            return self._beos_comp.Text()
    
    def _backend_selection(self):
        if self._beos_comp:
             return self._beos_comp.TextView().GetSelection()
    
    def _ensure_selection(self):
        if self._beos_comp:
            start, end = self._selection
            self._beos_comp.TextView().Select(start, end)
            
    def _ensure_text(self):
        if self._beos_comp:
            self._beos_comp.SetText(str(self.text))

    def _ensure_editable(self):
        if self._beos_comp:
            self._beos_comp.TextView().MakeEditable(self._editable)
    
    def _ensure_enabled_state(self):
        if self._beos_comp:
            self._beos_comp.SetEnabled(self._enabled)
    
    def _lost_focus(self):
        self.modify(text=self._beos_comp.Text())
    
    def _beos_clicked(self):
        send(self, 'enterkey')


class TextArea(ComponentMixin, AbstractTextArea):
    _beos_class = BScrollView.BScrollView
    _beos_sub_class = BTextView.BTextView
    _horizontal = 0
    _vertical = 1
    _beos_border = B_FANCY_BORDER
    
    def _ensure_created(self):
        self._focus = 0
        self._beos_id = str(self._beos_id)
        self._ensure_geometry()
        if self._beos_sub is None:
            self.sub_wrap(self._beos_sub_class(self._beos_bounds,
                           self._beos_id,
                           (0.0,0.0,self._beos_bounds[2], self._beos_bounds[3]),
                           self._beos_mode,
                           self._beos_flags))
            self._init_args = (self._beos_id,
                           self._beos_sub,
                           self._beos_mode,
                           self._beos_flags,
                           self._horizontal,
                           self._vertical,
                           self._beos_border)
        result = ComponentMixin._ensure_created(self)
        self._ensure_editable()
        self._ensure_enabled_state()
        self._ensure_text()
        return result
            
    def _ensure_text(self):
        if self._beos_comp:
            self._beos_sub.SetText(self.text)
    
    def _ensure_selection(self):
        if self._beos_comp:
            start, end = self._selection
            self._beos_sub.Select(start, end)

    def _ensure_geometry(self):
        self._beos_bounds = (float(self._x),
                float(self._y),
                float(self._width+ self._x-15),
                float(self._height+self._y))
    
    def _backend_selection(self):
        if self._beos_comp:
            start, end = self._beos_sub.GetSelection()
            return (start, end)
    
    def _backend_text(self):
        if self._beos_comp:
            return self._beos_sub.Text()
            
    def _ensure_editable(self):
        if self._beos_comp:
            self._beos_sub.MakeEditable(self._editable)

    def _lost_focus(self):
        self.modify(text=self._beos_sub.Text())
    
    def MakeFocus(self, focus=1):
        self._beos_sub.MakeFocus(focus)
        if not focus:
            self._lost_focus()        

#################################################################

class Frame(ComponentMixin, AbstractFrame):
    _beos_class = BView.BView
    
    def _ensure_created(self):
        self._beos_id = str(self._beos_id)
        self._ensure_geometry()
        self._init_args = (self._beos_bounds,
                           self._beos_id,
                           self._beos_mode,
                           self._beos_flags)
        result = ComponentMixin._ensure_created(self)
        for item in self._contents:
            if item._beos_comp is None:
                item._ensure_created()
        self._ensure_visibility()
        return result
    
    def _ensure_visibility(self):
        if self._beos_comp:
            if self._visible:
                if self._beos_comp.IsHidden():
                    self._beos_comp.Show()
            else:
                if self._beos_comp.IsHidden():
                    pass # Don't Hide stuff twice...
                else:
                    self._beos_comp.Hide()
        
    def _beos_add(self, object):
        self._beos_comp.AddChild(object._beos_comp)


class Window(ComponentMixin, AbstractWindow):
    _beos_class = BWindow.BWindow
    _beos_style = B_TITLED_WINDOW                       # See below for other styles
    _beos_flags = B_WILL_DRAW
    _beos_workspaces = B_CURRENT_WORKSPACE              # or B_ALL_WORKSPACES
    _style = 'default'
    _beos_styles = { 'default' : B_TITLED_WINDOW,
                     'document' : B_DOCUMENT_WINDOW,
                     'dialog' : B_MODAL_WINDOW,
                     'floating' : B_FLOATING_WINDOW,
                     'bordered' : B_BORDERED_WINDOW,
                     'other' : B_UNTYPED_WINDOW
                   }
    _focus = None
    
    def _ensure_created(self):
        if self._beos_comp is None:
            self._ensure_style()
            self._ensure_title()
            self._ensure_geometry()
            self.wrap(self._beos_class(
                      self._beos_bounds,
                      self._title,
                      self._beos_style,
                      self._beos_flags,
                      self._beos_workspaces))
            for item in self._contents:
                item._ensure_created()
            self._ensure_geometry()
            self._ensure_visibility()
            self._finish_creation()
                  
    def _ensure_title(self):
        if self._beos_comp:
            self._beos_comp.SetTitle(self._title)
    
    def _ensure_visibility(self):
        if self._beos_comp:
            self._beos_comp.Minimize(not self._visible)
    
    def _ensure_geometry(self):
        self._beos_bounds = (float(self._x)+10.0,     # Because these are inside
                             float(self._y)+30.0,     # values, not outside!
                             float(self._width), 
                             float(self._height))
        if self._beos_comp:
            self._beos_comp.MoveTo(self._beos_bounds[0], self._beos_bounds[1])
            self._beos_comp.ResizeTo(self._beos_bounds[2], self._beos_bounds[3])
    
    def _ensure_style(self):
        if self._beos_comp:
            self._beos_comp.SetType(self._beos_styles[self._style])
    
    def _beos_close_handler(self):
        #print "Destroy!"
        self.destroy()
        if self._beos_comp:
            self._beos_comp = None
    
    def QuitRequested(self):
        """
        This BeOS hook function is called whenever a quit type action is requested.
        Currently sends a Quit message to the app if it is the last window.
        """
        self._beos_close_handler()
        if BApplication.be_app.CountWindows() == 1:
            BApplication.be_app.PostMessage(B_QUIT_REQUESTED)
        return 1

    def MessageReceived(self, msg):
        """
        BeOS hook function - this function is called whenever a BMessage is received.
        The msg.what value tells us what type of BMessage it is.
        If the message is the right type, find the id of the object that created it, and
        call _beos_clicked() and _beos_lost_focus if applicable.
        """
        if msg.what == ACTION:
            #print "Received"
            id = msg.FindString('self_id')
            for item in self._contents:
                if item._beos_id == id:
                    if item._beos_clicked:    # Bit of a hack?
                        item._beos_clicked()
                        pass
                    if item._lost_focus:
                        item._lost_focus()

    def _ensure_title(self):
        if self._beos_comp:
            self._beos_comp.SetTitle(self._title)
        
    def _beos_add(self, object):
        self._beos_comp.AddChild(object._beos_comp)
    
    def _beos_remove(self, object):
        self._beos_comp.RemoveChild(object._beos_comp)
        
    def remove(self, object):
        if object in self._contents:
            self._beos_remove(object)
        AbstractWindow.remove(self, object)
        
    
###################################################################

class Application(WrapThis, AbstractApplication):
    _beos_running = 0

    def __init__(self):
        "Every application needs a constructor code.  What should this be?"
        AbstractApplication.__init__(self)
        self.wrap(BApplication.BApplication('application/python'))
            
    def ReadyToRun(self):
        for win in self._windows:
            win._beos_comp.Show()
                
    def OnInit(self):
        return 1
    
    def RefsReceived(self, msg):
        "BeOS hook function called when files dropped on our icon"
        # Don't know if this will work, since we don't really have an icon!
        print msg.refs
            
    def AboutRequested(self):
        about = BAlert.BAlert("About", __doc__, "Dismiss")
        about.Go()
    
    def add(self, win):
        AbstractApplication.add(self, win)
        #win._ensure_created()
        if self._beos_running:
            win._beos_comp.Show()
        
    def _mainloop(self):
        self._beos_running = 1
        self._beos_comp.Run()

    def QuitRequested(self):
        return 1
