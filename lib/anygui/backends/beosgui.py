"""

Okay, here is a working version of beosgui- except only applications and
windows are possible, and buttons are nearly there.


"""

import string

from anygui.backends import *
__all__ = anygui.__all__

#__all__ = ['factory']

############

import BAlert, BApplication
import BButton
import BCheckBox, BControl
import BFile, BFilePanel, BFont
import BList, BListItem, BListView                         # BList is NEW! (And Useless!)
import BMenuBar, BMenuItem, BMenu, BMessage
import BOutlineListView
import BPath, BPopUpMenu
import BRadioButton
import BScrollBar, BScrollView, BSeparatorItem, BSlider, BStatusBar, BStringItem, BStringView
import BTab, BTabView, BTextControl, BTextView
import BView, BVolume
import BWindow

from AppKit import *
from SupportKit import *
from InterfaceKit import *
from StorageKit import *

ACTION = 6666 # BMessage value
               
#################

class WrapThis:
    """Binds instance with BeOS API object.  Objects
that support this operation can call Python bound methods from
their virtual function ``hooks'', so things like MessageReceived()
work in Python.  Stolen blatantly from Donn."""

    def wrap(self, this):
        self._beos_comp = this
        self._beos_comp.bind(self)

    def sub_wrap(self, this):
        "For classes with scrollbox surrounding them."
        self._beos_sub = this
        self._beos_sub.bind(self)


#################################################################

class ComponentMixin(WrapThis):
    "Base class for all components."
    _height = -1 # default sizes & positions
    _width = -1
    _x = 0 # Note funny default for window positions.
    _y = 0 # (Works on inside of window, not outside).
    
    _action = None
    
    _beos_comp = None
    _beos_sub = None
    _beos_id = 0
    _beos_style = None
    _beos_msg = None
    _beos_mode = B_FOLLOW_LEFT + B_FOLLOW_TOP
    _beos_flags = B_WILL_DRAW + B_NAVIGABLE

    _init_args = None
    	
    def _ensure_created(self):
        application() # BeOS terminates processes that have no valid BApplication
        if self._beos_comp is None:
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
            self._beos_comp.ResizeToPreferred()
            #print self._beos_class, self._beos_id
            self._ensure_enabled_state()
            if self._container is not None:
                self._container._beos_add(self)
            ComponentMixin._beos_id += 1 # Gives each component a unique id
            return 1
        return 0
    
    def _is_created(self):
        return self._beos_comp is not None
    
    def _ensure_events(self):
        if self._action:
            self._beos_msg = BMessage.BMessage(ACTION)
            self._beos_msg.AddString('self_id', str(self._beos_id))

    def _ensure_geometry(self):
        self._beos_bounds = (float(self._x),
                float(self._y),
                float(self._width)*1.3, # Needs this?
                float(self._height))
        if self._beos_comp:
            self._beos_comp.ResizeToPreferred()


    def _ensure_visibility(self):
        pass
        
    def _ensure_enabled_state(self):
        pass

    def _ensure_destroyed(self):
        pass

    def _get_beos_text(self):
        # helper function for creation
        # returns the text required for creation.
        # This may be the _text property, or _title, ...,
        # depending on the subclass
        return self._text

#################################################################

class Label(ComponentMixin, AbstractLabel):
    """Designed for single lines of text only."""
    _beos_class = BStringView.BStringView
    #_beos_flags = B_WILL_DRAW
    _text = "BStringItem"
    #_width = 100
    
    def _ensure_created(self):
        self._beos_id = str(self._beos_id)
        self._init_args = (self._beos_bounds,
                           self._beos_id,
                           self._text,
                           self._beos_mode,
                           self._beos_flags)
        return ComponentMixin._ensure_created(self)
    
    def _ensure_created2(self):
        "Multiple Lines...Not Working Yet"
        self._beos_class = BTextView.BTextView
        self._beos_id = str(self._beos_id)
        self._init_args = (self._beos_bounds,
                           self._beos_id,
                           (0.0,0.0,self._beos_bounds[2], self._beos_bounds[3]),
                           self._beos_mode,
                           self._beos_flags)
        return ComponentMixin._ensure_created(self)
    
    def _ensure_text(self):
        if self._beos_comp:
            print self._text
            self._beos_comp.SetText(self._text)
            self._beos_comp.ResizeToPreferred()

##################################################################

                      
class ListBox(ComponentMixin, AbstractListBox):
    _beos_sub_class = BListView.BListView
    _beos_type = B_SINGLE_SELECTION_LIST
    _beos_mode = B_WILL_DRAW + B_NAVIGABLE + B_FRAME_EVENTS
    _beos_class = BScrollView.BScrollView
    _beos_flags = 0
    _horizontal = 0
    _vertical = 1
    _beos_border = B_FANCY_BORDER
    
    def SelectionChanged(self):
        if self._action:
            self._action()
    
    def _ensure_created(self):
        "With Scroll Bars."
        self._beos_id = str(self._beos_id)
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
            temp = ComponentMixin._ensure_created(self)
            self._ensure_items()
            self._ensure_selection()
            return temp
    
    def _ensure_created2(self):
        "Without Scroll Bars."
        self._beos_class = BListView.BListView
        self._beos_id = str(self._beos_id)
        self._init_args = (self._beos_bounds,
                           str(self._beos_id),
                           self._beos_type,
                           self._beos_mode,
                           self._beos_flags)
        temp = ComponentMixin._ensure_created(self)
        self._beos_sub = self._beos_comp
        self._ensure_items()
        return temp

        
    def _backend_items(self):
        if self._beos_comp:
            items = []
            for index in range(self._beos_sub.CountItems()):
                items.append(self._beos_sub.ItemAt(index).Text())
            return items
    
    def _backend_selection(self):
        if self._beos_comp:
            return self._beos_sub.CurrentSelection()
            
    def _ensure_items(self):
        if self._beos_comp:
            self._beos_sub.MakeEmpty()
            for item in self._items:
                self._beos_sub.AddItem(BStringItem.BStringItem(str(item)))
    
    def _ensure_selection(self):
        if self._beos_comp:
            self._beos_sub.Select(self._selection)

###################################################################

class Button(ComponentMixin, AbstractButton):
    _beos_class = BButton.BButton
    
    def _ensure_text(self):
        if self._beos_comp:
    	    self._beos_comp.SetLabel(self._text)

    def _ensure_enabled_state(self):
        if self._beos_comp:
            self._beos_comp.SetEnabled(self._enabled)

class ToggleButtonMixin(ComponentMixin):

    def _ensure_state(self):
        if self._beos_comp is not None:
            self._beos_comp.this.SetValue(self._on)

    def _ensure_enabled_state(self):
        if self._beos_comp:
            self._beos_comp.SetEnabled(self._enabled)
            
    def _get_on(self):
        return self._beos_comp.Value()

     
class CheckBox(ToggleButtonMixin, AbstractCheckBox):
    _beos_class = BCheckBox.BCheckBox
    

class RadioButton(ToggleButtonMixin, AbstractRadioButton):
    "Radio Group Not Working - need a seperate BView for each group."
    _beos_class = BRadioButton.BRadioButton
    
class BRadioGroup(RadioGroup, ComponentMixin):
    _beos_class = BView.BView
    _beos_bounds = (0.0,0.0,100.0,100.0)
    
    def _ensure_created(self):
        self._beos_id = str(self._beos_id)
        print self._beos_id
        self._init_args = (self._beos_bounds,
                           self._beos_id,
                           self._beos_mode,
                           self._beos_flags)
        return ComponentMixin._ensure_created(self)
        
#################################################################


class TextField(ComponentMixin, AbstractTextField):
    _beos_class = BTextControl.BTextControl
    _label = "Label"
    _text = "Edit Me..."
    
    def _ensure_created(self):
        self._beos_id = str(self._beos_id)
        #self._ensure_events()
        self._init_args = (self._beos_bounds,
                           self._beos_id,
                           self._label, # !!!
                           self._text,
                           self._beos_msg,
                           self._beos_mode,
                           self._beos_flags)
        return ComponentMixin._ensure_created(self)
                           
    def _backend_text(self):
        if self._beos_comp:
            return self._beos_comp.Text()
    
    def _backend_selection(self):
        if self._beos_comp:
            pass
            #print dir(self._beos_comp.TextView())
            #return self._beos_comp.TextView().GetSelection()
    
    def _ensure_selection(self):
        if self._beos_comp:
            start, end = self.selection
            self._beos_comp.TextView().Select(start, end)
            
    def _ensure_text(self):
        if self._beos_comp:
            self._beos_comp.TextView().SetText(self.text)

    def _ensure_editable(self):
        if self._beos_comp:
            self._beos_comp.MakeEditable(self._editable)

class TextArea(ComponentMixin, AbstractTextArea):
    _beos_class = BScrollView.BScrollView
    _beos_sub_class = BTextView.BTextView
    _horizontal = 0
    _vertical = 1
    _beos_border = B_FANCY_BORDER
    
    def _ensure_created(self):
        self._beos_id = str(self._beos_id)
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
        temp = ComponentMixin._ensure_created(self)
        #self._beos_sub.SetDoesUndo(1)
        return temp
    
    def _ensure_created2(self):
        self._beos_id = str(self._beos_id)
        self._beos_class = self._beos_sub_class
        self._init_args = (self._beos_bounds,
                           self._beos_id,
                           (0.0,0.0, self._beos_bounds[2], self._beos_bounds[3]),
                           self._beos_mode,
                           self._beos_flags)
        temp = ComponentMixin._ensure_created(self)
        self._beos_sub = self._beos_comp
        return temp
        
    def _ensure_text(self):
        if self._beos_comp:
            self._beos_sub.SetText(self._text)
            #self._beos_comp.Draw((0.0,0.0,1000.0,100.0))
    
    def _ensure_selection(self):
        if self._beos_comp:
            start, end = self._selection
            self._beos_sub.Select(start, end)
    
    def _backend_selection(self):
        if self._beos_comp:
            start, end = 0, 0
            #self._beos_sub.GetSelection(start, end)
            return (start, end)
    
    def _backend_text(self):
        if self._beos_comp:
            return self._beos_sub.Text()
    
    def _ensure_editable(self):
        if self._beos_comp:
            self._beos_sub.MakeEditable(self._editable)

#################################################################

class Window(ComponentMixin, AbstractWindow):
    _beos_class = BWindow.BWindow
    _beos_style = B_TITLED_WINDOW
    _beos_flags = B_WILL_DRAW
    _beos_workspaces = B_CURRENT_WORKSPACE
    _beos_styles = { 'default' : B_TITLED_WINDOW,
                     'document' : B_DOCUMENT_WINDOW,
                     'dialog' : B_MODAL_WINDOW,
                     'floating' : B_FLOATING_WINDOW,
                     'bordered' : B_BORDERED_WINDOW,
                     'other' : B_UNTYPED_WINDOW
                   }
    
    def _ensure_created(self):
        self._ensure_style()
        self._ensure_title()
        self._ensure_visibility()
        self._ensure_geometry()
        if self._beos_comp is None:
            self.wrap(self._beos_class(
                      self._beos_bounds,
                      self._title,
                      self._beos_style,
                      self._beos_flags,
                      self._beos_workspaces))
                      
    def _ensure_title(self):
        if self._beos_comp:
            self._beos_comp.SetTitle(self._title)
    
    def _ensure_visibility(self):
        if self._beos_comp:
            if self._visible:
                self._beos_comp.Show()
                #self._beos_comp.Minimize(0) # Prefer #
            else:
                if not self._beos_comp.IsHidden():
                    self._beos_comp.Hide()
                #self._beos_comp.Minimize(1) # Prefer #
    
    def _ensure_geometry(self):
        self._beos_bounds = (float(self._x)+10.0, # Because these are inside
                             float(self._y)+30.0, # values, not outside!
                             float(self._width)*1.25, # Not Wide enough...?
                             float(self._height))
        if self._beos_comp:
            self._beos_comp.MoveTo(float(self._x)+10, float(self._y)+30)
            self._beos_comp.ResizeTo(float(self._width)*1.25, float(self._height))
    
    def _ensure_style(self):
        try:
            self._beos_style = self._beos_styles[self._style]
        except:
            pass
        if self._beos_comp:
            self._beos_comp.SetType(self._beos_style)
            
    def QuitRequested(self):
        BApplication.be_app.PostMessage(B_QUIT_REQUESTED)
        return 1

    def MessageReceived(self, msg):
        if msg.what == ACTION:
            id = msg.FindString('self_id')
            print id
            for item in self._contents:
                if item._beos_id == id:
                    item._action()

    
    def _ensure_title(self):
        if self._beos_comp:
            self._beos_comp.SetTitle(self._title)
        
    def add(self, object):
        if self._beos_comp is None:
            self._ensure_created()
        if object._beos_comp is None:
            print object, object.geometry
            object._ensure_geometry()
            object._ensure_created()
        #print issubclass(object._beos_class, BListView.BListView)
        self._beos_comp.AddChild(object._beos_comp)
        AbstractWindow.add(self, object)

    
###################################################################

class Application(WrapThis, AbstractApplication):
    def __init__(self):
        AbstractApplication.__init__(self)
        self.wrap(BApplication.BApplication('application/python'))
            
    def ReadyToRun(self):
        for win in self.windows():
            win._ensure_visibility()
    
    def OnInit(self):
        return 1
    
    def _mainloop(self):
        self._beos_comp.Run()
    


#####################################################################

class factory:
    _map = {'Window': Window,
            'Button': Button,
            'RadioButton': RadioButton,
            'RadioGroup': BRadioGroup,
            'CheckBox': CheckBox,
            'Application': Application,
            'Label': Label,
            'ListBox': ListBox,
            'TextField': TextField,
            'TextArea': TextArea,
            }
    def get_class(self, name):
        return self._map[name]

