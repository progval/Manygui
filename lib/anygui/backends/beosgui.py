"""
beosgui.py, a part of anygui that allows anygui applications to directly drive BeOS GUI functions.

beosgui.py (possibly) requires Bethon (0.3), Python (2.2) and BeOS (5.0) to function.
Bethon can be found at:  www.bebits.net/app/1564
Python can be found at:  www.python.org
BeOS might be found at:  free.be.com
           
beosgui.py is the work of Matthew Schinckel, and the WrapThis feature is the work of Donn Cave.

This version of beosgui.py (and the anygui it is part of) are a work in progress.  Please visit anygui.sf.net to see if there is a newer version.

29/08/2001
"""

TODO = """
To Do List:

Make Label actually a TextArea - to allow multiple lines.

Make RadioGroups work.
Stage 1: dodgy system assuming only one group per window [DONE]
Stage 2: proper system using seperate BViews for each group

Find out why the 2 text areas are on top of one another in
test/test_textarea.py.  Suspect place bug, since changing sizes
fixes the problem.

Put more comments - with the other available values, ie in
_beos_mode, _beos_flags, etc.

Read through the BeBook looking for more info that might be useful.
(May need to work on some more *.dx files...)

New Classes to implement:

Alert, FilePanel, Menu, Slider, StatusBar, TabView

OutlineListView, PopUpMenu, ColourControl

+

implement ScrollView and make ListView/TextView use the class

"""

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
import BWindow                                             # Version with Minimize()

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
        #app = Application() # BeOS terminates processes that have no valid BApplication
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
            self._beos_msg = BMessage.BMessage(ACTION) # Create a BMessage instance
            self._beos_msg.AddString('self_id', str(self._beos_id)) # Add the id of the object
            # also need to add the args and keywords ?

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
    _beos_flags = B_WILL_DRAW
    _text = "BStringItem"
    
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
        result = ComponentMixin._ensure_created(self)
        self._ensure_text()
        print self._text
        return result
    
    def _ensure_text(self):
        if self._beos_comp:
            self._beos_comp.SetText(self._text)
            self._beos_comp.ResizeToPreferred()

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
    
    # BeOS hook function
    #def SelectionChanged(self):
    #    """Replaced by InvocationMessage."""
    #    if self._action:
    #        self._action()
    
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
            result = ComponentMixin._ensure_created(self)
            self._ensure_items()
            self._ensure_selection()
            self._ensure_events()
            return result
    
    def _ensure_created2(self):
        "Without Scroll Bars."
        self._beos_class = BListView.BListView
        self._beos_id = str(self._beos_id)
        self._init_args = (self._beos_bounds,
                           str(self._beos_id),
                           self._beos_type,
                           self._beos_mode,
                           self._beos_flags)
        result = ComponentMixin._ensure_created(self)
        self._beos_sub = self._beos_comp
        self._ensure_items()
        self._ensure_events()
        return result

        
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
    
    def _ensure_events(self):
        if self._beos_comp:
            ComponentMixin._ensure_events(self)
            self._beos_sub.SetInvocationMessage(self._beos_msg)
            
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
            self._beos_comp.SetValue(self._on)

    def _ensure_enabled_state(self):
        if self._beos_comp:
            self._beos_comp.SetEnabled(self._enabled)
            
    def _get_on(self):
        return self._beos_comp.Value()

     
class CheckBox(ToggleButtonMixin, AbstractCheckBox):
    _beos_class = BCheckBox.BCheckBox


class RadioButton(ToggleButtonMixin, AbstractRadioButton):
    _beos_class = BRadioButton.BRadioButton


class BRadioGroup(RadioGroup):
    _beos_class = BView.BView #Not yet used :)
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
            btn.action = self._action
            
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
        self._items = []
        self.add(items)

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        if self._value != value:
            self._value = value
            for item in self._items:
                item._update_state()
            self.do_action()

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
            start, end = self._beos_comp.TextView().GetSelection()
            # Supposed to pass  (2 x) pointer to int, and have no return.
            #  Still trying to get this to work :-)
            return (start, end)
    
    def _ensure_selection(self):
        if self._beos_comp:
            start, end = self._selection
            self._beos_comp.TextView().Select(start, end)
            
    def _ensure_text(self):
        if self._beos_comp:
            self._beos_comp.SetText(self._text)

    def _ensure_editable(self):
        if self._beos_comp:
            self._beos_comp.TextView().MakeEditable(self._editable)
    
    def _ensure_enabled_state(self):
        if self._beos_comp:
            self._beos_comp.SetEnabled(self._enabled)


class TextArea(ComponentMixin, AbstractTextArea):
    _beos_class = BScrollView.BScrollView
    _beos_sub_class = BTextView.BTextView
    _horizontal = 0
    _vertical = 1
    _beos_border = B_FANCY_BORDER
    
    def _ensure_created(self):
        "Within Scroll Boxes"
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
        result = ComponentMixin._ensure_created(self)
        self._ensure_editable()
        self._ensure_enabled_state()
        self._ensure_text()
        return result
    
    def _ensure_created2(self):
        "No Scroll Boxes"
        self._beos_id = str(self._beos_id)
        self._beos_class = self._beos_sub_class
        self._init_args = (self._beos_bounds,
                           self._beos_id,
                           (0.0,0.0, self._beos_bounds[2], self._beos_bounds[3]),
                           self._beos_mode,
                           self._beos_flags)
        result = ComponentMixin._ensure_created(self)
        self._beos_sub = self._beos_comp
        return result
        
    def _ensure_text(self):
        if self._beos_comp:
            self._beos_sub.SetText(self._text)
    
    def _ensure_selection(self):
        if self._beos_comp:
            start, end = self._selection
            self._beos_sub.Select(start, end)
    
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

#################################################################

class Window(ComponentMixin, AbstractWindow):
    _beos_class = BWindow.BWindow
    _beos_style = B_TITLED_WINDOW
    _beos_flags = B_WILL_DRAW
    _beos_workspaces = B_CURRENT_WORKSPACE # or B_ALL_WORKSPACES
    _style = 'default'
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
            self._beos_comp.Minimize(not self._visible)
    
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
            #print self._style
            self._beos_style = self._beos_styles[self._style]
        except:
            pass
        if self._beos_comp:
            self._beos_comp.SetType(self._beos_style)
            
    def QuitRequested(self):
        """
        This BeOS hook function is called whenever a quit type action is requested.
        
        Currently sends a Quit message to the app if it is the last window.
        
        #### LIKELY TO CHANGE ####
        
        """
        if BApplication.be_app.CountWindows() == 1:
            BApplication.be_app.PostMessage(B_QUIT_REQUESTED)
        return 1

    def MessageReceived(self, msg):
        """
        BeOS hook function - this function is called whenever a BMessage is generated.
        The msg.what value tells us what type of BMessage it is.  We are only interested
        at this stage in those that have been defined as a self._action function.
        If the message is the right type, find the id of the object that created it, and
        call the function/method that is that object's _current_ action.
        """
        if msg.what == ACTION:
            id = msg.FindString('self_id')
            for item in self._contents:
                if item._beos_id == id:
                    #print item._action.__name__
                    item._action()

    
    def _ensure_title(self):
        if self._beos_comp:
            self._beos_comp.SetTitle(self._title)
        
    def add(self, object):
        if self._beos_comp is None:
            self._ensure_created()
        if object._beos_comp is None:
            object._ensure_geometry()
            object._ensure_created()
        """
        if object._beos_class == RadioButton._beos_class: ###HACK CITY
            if object.group:
                if object.group._beos_comp is None:
                    object.group._ensure_created()
                    self._beos_comp.AddChild(object.group._beos_comp)
                object.group.add([object])
                object.group._ensure_geometry()
            else:
                self._beos_comp.AddChild(object._beos_comp)
        else:
        """
        self._beos_comp.AddChild(object._beos_comp)
        AbstractWindow.add(self, object)
    
    def show(self):
        AbstractWindow.show(self)
        self._ensure_visibility()
    
    def hide(self):
        AbstractWindow.show(self)
        self._ensure_visibility()
    
###################################################################

class Application(WrapThis, AbstractApplication):

    def __init__(self):
        "Every application needs a constructor code.  What should this be?"
        AbstractApplication.__init__(self)
        self.wrap(BApplication.BApplication('application/python'))
            
    def ReadyToRun(self):
        for win in self.windows():
            win._beos_comp.Show()
                
    def OnInit(self):
        return 1
    
    def RefsReceived(self, msg):
        "BeOS hook function supposedly called when files dropped on our icon"
        print msg.refs
    
    def AboutRequested(self):
        about = BAlert.BAlert("About", __doc__, "Dismiss")
        about.Go()
    
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

