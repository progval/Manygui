"""
beosgui.py is a backend for Manygui, using Bethon 0.5 (BeOS API wrappers).

Developed by Matthew Schinckel <matt@null.net>
"""

TODO = '''
#==========================================================================#
# TODO List

. Fix Command-Q Quitting Bug (again).
. Create List/Scroll View wrappers. [DONE]
. Create Text-based wrappers. [DONE]
. Check Frame wrapper.
. Fix RadioGroup problems.
. Create FileDialog / AboutDialog.
. Create Menus.
. Figure out sizes/placement stuff. *****
. Remove/Improve Comments.
. Refactor where possible.
. Run Tests, Report.

'''

#==========================================================================#
# Manygui Imports

# Import Manygui infrastructure.
from manygui.backends import *
from manygui.Applications import AbstractApplication
from manygui.Wrappers import AbstractWrapper
from manygui.Events import *
from manygui.Exceptions import Error
from manygui.Utils import log
from manygui import application
# End Manygui imports.

#==========================================================================#
# Bethon Imports

# All Bethon modules are imported.  Not all are used.
import BAlert, BAppFileInfo, BApplication
import BBitmap, BBox, BButton
import BCheckBox, BControl, BColorControl
import BDirectory
import BEntry
import BFile, BFilePanel, BFont
import BHandler
import BInvoker
import BListItem, BListView, BLocker, BLooper
import BMenuBar, BMenuItem, BMenu, BMessage, BMessageRunner, BMimeType
import BNode, BNodeInfo
import BOutlineListView
import BPath, BPopUpMenu
import BRadioButton, BRoster
import BScrollBar, BScrollView, BSeparatorItem, BSerialPort, BSlider, BStatable, BStatusBar, BStringItem, BStringView
import BTab, BTabView, BTextControl, BTextView
import BView, BVolume
import BWindow

from AppKit import *
from SupportKit import *
from InterfaceKit import *
from StorageKit import *

ACTION = 6666 # BMessage value

# End backend API imports.

#==========================================================================#
# What's In Here?

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

# temporary version...
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
  GroupBoxWrapper
'''.split()

#==========================================================================#
# Base Class for all widgets

class ComponentWrapper(AbstractWrapper):
    _beos_id = 0
    _beos_style = None
    _beos_msg = None
    _beos_mode = B_FOLLOW_LEFT + B_FOLLOW_TOP
    _beos_flags = B_WILL_DRAW + B_NAVIGABLE
    
    _init_args = None
    
    """
    The ComponentWrapper class should abstract away all behavior
    that (nearly) all backend widgets perform similarly. Normally,
    this will include geometry and visibility management, and in some
    cases widget creation can be handled here as well (see wxgui.py
    for example).
    """
    
    def __init__(self, *args, **kwds):
        """
        Common widget wrapper initialization code. The main thing that
        we would normally do here is set any backend-specific
        attribute constraints.
        
        Whenever the application code alters a widget proxy, the front end
        will "push" any changed widget attributes into the backend by
        calling the wrapper.set<Attribute>(self,new_value) method for any
        attribute that changes. The setContraints() method allows the
        backend to specify the order in which the set<Attribute>()
        method calls are made, by specifying the order in which attribute
        names are set. The constraints set here are just examples.
        However, it is almost certainly a good idea to ensure that
        'container' is set before any other attribute, so at minimum
        you should call "self.setConstraints('container')" here.
        """
        AbstractWrapper.__init__(self, *args, **kwds)

        # 'container' before everything, then geometry.
        self.setConstraints('container','x','y','width','height')

        # addConstraint(self,before,after) adds a constraint that attribute
        # 'before' must be set before 'after', when both appear in the
        # same push operation. An attempt to set mutually contradictory
        # constraints will result in an exception.
        self.addConstraint('geometry', 'visible')

    def widgetFactory(self,*args,**kws):
        """
        Create and return the backend widget for this wrapper.
        The value returned will be immediately assigned to self.widget
        by the Manygui framework; henceforth you should refer to self.widget.
        """
        if hasattr(self.proxy.container,'wrapper'):
            parent = self.proxy.container.wrapper._getContainer()
        else:
            parent = None
        if self._beos_class is None:
            raise NotImplementedError('Not Implemented in beosgui yet')
        else:
            self._beos_id = str(self._beos_id)
            if self._init_args is None:
                self._beos_bounds = self.getGeometry()
                self._text = self.proxy.state['text']
                self._init_args = (self._beos_bounds,
                                   self._beos_id,
                                   self._text,
                                   self._beos_msg,
                                   self._beos_mode,
                                   self._beos_flags)
            widget = self._beos_class(*self._init_args)
            print(widget)
            print('\t', widget.Frame())
            print('\t', self._beos_bounds)
            ComponentWrapper._beos_id += 1
            return widget

    def enterMainLoop(self): # ...
        """ enterMainLoop() is called when the application event loop is
        started for the first time. """
        #self.proxy.push()
        #if self.widget is None: return
        #self.widget.show()

    def destroy(self):
        """
        destroy() is called when the application needs to destroy the
        native widget. You can also call it within the wrapper code if
        you need to destroy your native widget for some reason. 
        """
        #self.widget = DummyWidget()
        self.widget = None
        #raise NotImplementedError, 'should be implemented by subclasses'

    # From here on, all methods in this class are getters and setters.
    # Setters must be implemented; they are called automatically in
    # response to application-code manipulation of the associated
    # proxy object, and perform the required magic on self.widget
    # to implement the change.
    #
    # Getters need not be implemented unless the backend requires
    # special handling, or if the attribute in question can be changed
    # by user actions as well as by application code. Getters are
    # called automatically during proxy attribute access, if they
    # exist; otherwise the last value set in the proxy is returned.
    # This file provides empty getter definitions for those attributes
    # that will nearly always require special handling for get
    # operations.
    #
    # The setters and getters here are a typical example of
    # attribute handling that's common to all of a backend's
    # widgets. For example, getGeometry() and setGeometry() work
    # the same for any backend widget, thus they're included
    # here in the common wrapper base class.
    #
    # Note that you must implement all the setter and getter
    # methods in this file in order for your backend to work
    # properly!

    def setContainer(self,container):
        """
        setContainer() is called whenever the proxy's container (the
        Frame or top-level Window) in which the widget will appear is
        set. It's called implicitly when a widget is added to a
        container via the container.add(widget) method.

        In most backends, you'll call self.create() here in order to
        actually create the backend widget. create() is a template
        method that calls self.widgetFactory() to create the widget,
        and then performs some bookkeeping for the wrapper.

        When the widget is removed from its container, setContainer()
        will be called with container==None; you must handle that case
        correctly, whatever that means for your backend.
        """
        
        if self.widget is None:
            # If the container has changed, and there's already a native
            # widget, it may be necessary to take special action here.
            pass
        # Be sure to handle any backend container/contents protocol
        # here!
        # ...
        
        if container is not None:
            parent = container.wrapper.widget
            self.create(parent)
            parent.AddChild(self.widget)
        else:
            if self.widget is not None:
                self.widget.Window().RemoveChild(self.widget)

        # Ensure native widget is brought up to date wrt the proxy
        # state.
        #self.proxy.push(blocked=['container'])
        #raise NotImplementedError, 'should be implemented by subclasses'

    def setGeometry(self,x,y,width,height):
        """ Set the native widget's geometry. Note that we call
        self.noWidget() here to see if the wrapper has a native widget
        to manage. You should probably use this idiom at the start of
        all setter and getter methods, unless you have a very good
        reason not to. """
        if self.widget is None: return
        self.widget.MoveTo(float(x), float(y))
        self.widget.ResizeTo(float(width), float(height))
        
    def getGeometry(self):
        """ Get the native widget's geometry as an (x,y,w,h) tuple.
        Since the geometry can be changed by the user dragging the
        window frame, you must implement this method. """
        if self.widget is None:
            return (self.proxy.state['x'],
                    self.proxy.state['y'],
                    self.proxy.state['width'],
                    self.proxy.state['height'])
        return self.widget.Frame()

    def setVisible(self,visible):
        """ Set/get the native widget's visibility. """
        if self.widget is None: return
        if visible:
            if self.widget.IsHidden():
                self.widget.Show()
        else:
            if not self.widget.IsHidden():
                self.widget.Hide()

    def setEnabled(self,enabled):
        """ Set/get the native widget's enabled/disabled state. """
        if self.widget is None: return
        self.widget.SetEnabled(enabled)
        #raise NotImplementedError, 'should be implemented by subclasses'

    def setText(self,text):
        """ Set/get the text associated with the widget. This might be
        window title, frame caption, label text, entry field text,
        or whatever.
        """
        if self.widget is None: return
        raise NotImplementedError('should be implemented by subclasses')

#==========================================================================#
# Label

class LabelWrapper(ComponentWrapper):
    """
    Wraps a backend "label" widget - static text.
    You may need to implement setText() here.
    """
    _beos_class = BStringView.BStringView
    _beos_flags = B_WILL_DRAW
    _text = "BStringView"
    
    def widgetFactory(self,*args,**kws):
        self._beos_bounds = self.getGeometry()
        self._text = self.proxy.state['text']
        self._init_args = (self._beos_bounds,
                           str(self._beos_id),
                           str(self._text),
                           int(self._beos_mode),
                           int(self._beos_flags))
        return ComponentWrapper.widgetFactory(self,*args,**kws)
    
    def setText(self, text):
        if self.widget is None: return
        self.widget.SetText(text)
        
    def widgetSetUp(self):
        pass
    
#==========================================================================#
# ListBox

class ListBoxWrapper(ComponentWrapper):
    """
    Wraps a backend listbox.

    At the moment, Manygui supports only single-select mode.
    """
    _beos_class = BScrollView.BScrollView
    _beos_sub_class = BListView.BListView
    _beos_type = B_SINGLE_SELECTION_LIST
    _beos_mode = B_WILL_DRAW + B_NAVIGABLE + B_FRAME_EVENTS #+ B_FOLLOW_ALL_SIDES #??
    _beos_border = B_FANCY_BORDER
    _beos_flags = 0
    _h_scroll = 0
    _v_scroll = 1
    _beos_sub = None
    
    def widgetFactory(self,*args,**kwds):
        self._beos_bounds = list(self.getGeometry())
        self._beos_bounds[3] -= 15
        self._beos_bounds[2] *= 1.4
        self._beos_bounds = tuple(self._beos_bounds)
        self._beos_sub = self._beos_sub_class(self._beos_bounds,
                                              str(self._beos_id)+"_sub",
                                              self._beos_type,
                                              self._beos_mode,
                                              self._beos_flags)
        self._init_args = (str(self._beos_id),
                           self._beos_sub,
                           self._beos_mode,
                           self._beos_flags,
                           self._h_scroll,
                           self._v_scroll,
                           self._beos_border)
        return ComponentWrapper.widgetFactory(self,*args,**kwds)

    def setItems(self,items):
        """
        Set the contents of the listbox widget. 'items' is a list of
        strings, or of str()-able objects.
        """
        if self._beos_sub is None: return
        self._beos_sub.MakeEmpty()
        for item in items:
            self._beos_sub.AddItem(BStringItem.BStringItem(str(item)))

    def getItems(self):
        """
        Return ths listbox contents, in order, as a list of strings.
        """
        if self._beos_sub is None: return
        return self._beos_sub.Items()
        

    def setSelection(self,selection):
        """
        Set the selection. 'selection' is an integer indicating the
        item to be selected.
        """
        if self._beos_sub is None: return
        self._beos_sub.Select(selection)

    def getSelection(self):
        """
        Return the selected listbox item index as an integer.
        """
        if self._beos_sub is None: return
        return self._beos_sub.CurrentSelection()

    def widgetSetUp(self):
        """
        widgetSetUp() is called by the Manygui framework immediately after
        the native widget has been created and assigned to self.widget.
        The most common use of widgetSetUp() is to register any event
        handlers necessary to deal with user actions.

        The ListBox widget requires that an Manygui 'select' event be
        fired whenever the user selects an item of the listbox.
        self._select() sends the event, so here you should associate
        the back-end's selection event with the self._select method.
        """
        self.setItems(self.proxy.state['items'])
        self.setSelection(self.proxy.state['selection'])
        self._beos_sub.bind(self)
        # Select
        self._beos_msg = BMessage.BMessage(ACTION)
        self._beos_msg.AddString('self_id', str(self._beos_id))
        self._beos_msg.AddString('event', 'select')
        self._beos_sub.SetSelectionMessage(self._beos_msg)
        # Invoke (Double Click)
        self._beos_msg = BMessage.BMessage(ACTION)
        self._beos_msg.AddString('self_id', str(self._beos_id))
        self._beos_msg.AddString('event', 'invoke')
        self._beos_sub.SetInvocationMessage(self._beos_msg)

    def _select(self,*args):
        """
        Send an Manygui 'select' event when the user clicks or otherwise
        selects a listbox item. Note that the source of the event is
        self.proxy, not self; that's because application code only
        knows about proxies, not wrappers, so the source of the Manygui
        event must be a proxy.
        """
        send(self.proxy,'select')
    
    #def SelectionChanged(self):
    #    send(self.proxy, 'select')

#==========================================================================#
# Canvas

#class CanvasWrapper(ComponentWrapper):
# Fix me!
#    _twclass = tw.Canvas

#==========================================================================#
# Button

class ButtonWrapper(ComponentWrapper):
    """
    Wraps a backend command-button widget - the kind you click
    on to initiate an action, eg "OK", "Cancel", etc.
    """
    
    _beos_class = BButton.BButton
    
    def setText(self,text):
        if self.widget is None: return
        self.widget.SetLabel(str(text))

    def widgetSetUp(self):
        """
        Register a backend event handler to call self.click when
        the user clicks the button.
        """
        #print self._beos_bounds
        #self.setGeometry(*self._beos_bounds)
        #print self.widget.Frame()
    
    def widgetFactory(self,*args,**kwds):
        self._beos_msg = BMessage.BMessage(ACTION)
        self._beos_msg.AddString('self_id', str(self._beos_id))
        self._beos_msg.AddString('event', 'click')
        return ComponentWrapper.widgetFactory(self,*args,**kwds)        

    def _click(self,*args,**kws):
        send(self.proxy,'click')

#==========================================================================#
# Base Class for 'State' buttons

class ToggleButtonMixin(ButtonWrapper):
    """
    Checkboxes and radio buttons often have common behavior that can
    be abstracted away; on the other hand, sometimes they don't.
    Consider this an example only.

    They also should generate 'click' events, so we'll just inherit
    ButtonWrapper here to get the event setup code. Your backend
    may not permit this, however; do what needs to be done.
    """

    def getOn(self):
        """ Return the button's state: 1 for checked, 0 for not. """
        if self.widget is None: return
        return self.widget.Value()

    def setOn(self,on):
        """ Set the button's state. """
        if self.widget is None: return
        self.widget.SetValue(on)
        
#==========================================================================#
# CheckBox

class CheckBoxWrapper(ToggleButtonMixin):
    """
    Usually ToggleButtonMixin completely handles the CheckBox
    behavior, but in case it doesn't, you may need to write some
    code here.
    """
    _beos_class = BCheckBox.BCheckBox

#==========================================================================#
# Radio Button

class RadioButtonWrapper(ToggleButtonMixin):
    """
    Radio buttons are a pain. Only one member of an RB "group" may be
    active at a time. Manygui provides the RadioGroup front-end
    class, which takes care of querying the state of radiobuttons
    and setting their state in a mutually exclusive manner.
    However, many backends also enforce this mutual exclusion,
    which means that things can get complicated. The RadioGroup
    class is implemented in as non-intrusive a way as possible,
    but it can be a challenge to arrange for them to act in
    the correct way, backend-wise. Look at the other backend
    implementations for some clues.

    In the case where a backend implements radiobuttons as a simple
    visual variant of checkboxes with no mutual-exclusion behavior,
    this class already does everything you need; just create the
    proper backend widget in RadioButtonWrapper.widgetFactory(). You
    can usually fake that kind of backend implementation by playing
    tricks with the backend's mutual-exclusion mechanism. For example,
    create a tiny frame to encapsulate the backend radiobutton, if
    your backend enforces mutual exclusion on a per-frame basis.
    """
    groupMap = {}
    _beos_class = BRadioButton.BRadioButton

    def setGroup(self,group):
        if group is None:
            return
        if self.proxy not in group._items:
            group._items.append(self.proxy)

#==========================================================================#
# Base Class for Text Widgets

class TextControlMixin:
    """
    Single-line entry fields and multiline text controls usually
    have a lot of common behavior that can be abstracted away. Do
    that here.
    """
    def widgetSetUp(self):
        """
        Arrange for a press of the "Enter" key to call self._return.
        """
        if self._beos_sub is None:
            self._beos_sub = self.widget.TextView()
        self.setEditable(self.proxy.state['editable'])

    def setText(self,text):
        """ Set/get the text associated with the widget. This might be
        window title, frame caption, label text, entry field text,
        or whatever.
        """
        if self.widget is None: return
        try:
            self.widget.SetText(text)
        except:
            pass
        if self._beos_sub is None: return
        self._beos_sub.SetText(text)

    def getText(self):
        """
        Fetch the widget's associated text. You *must* implement this
        to get the text from the native widget; the default getText()
        from ComponentWrapper (almost) certainly won't work.
        """
        if self.widget is None: return
        try:
            return self.widget.Text()
        except:
            pass
        if self._beos_sub is None: return
        return self._beos_sub.Text()

    def getSelection(self):
        if self._beos_sub is None: return
        return self._beos_sub.GetSelection()
    
    def setSelection(self, selection):
        if self._beos_sub is None: return
        start, end = selection
        self._beos_sub.Select(start,end)
    
    def setEditable(self, editable):
        if self._beos_sub is None: return
        self._beos_sub.MakeEditable(editable)
        try:
            self.widget.SetEnabled(editable)
        except:
            pass

#==========================================================================#
# TextField

class TextFieldWrapper(TextControlMixin,ComponentWrapper):
    """
    Wraps a native single-line entry field.
    """
    _beos_class = BTextControl.BTextControl
    _beos_label = None
    _beos_sub = None
    
    def widgetFactory(self,*args,**kwds):
        self._beos_bounds = self.getGeometry()
        self._text = self.proxy.state['text']
        self._beos_msg = BMessage.BMessage(ACTION)
        self._beos_msg.AddString('self_id', str(self._beos_id))
        self._beos_msg.AddString('event', 'enterkey')
        self._init_args = (self._beos_bounds,
                           str(self._beos_id),
                           self._beos_label, # Currently None
                           self._text,
                           self._beos_msg,
                           self._beos_mode,
                           self._beos_flags)
        return ComponentWrapper.widgetFactory(self,*args,**kwds)        

    def _return(self,*args,**kws):
        send(self.proxy, 'enterkey')

#==========================================================================#
# TextArea

class TextAreaWrapper(TextControlMixin,ComponentWrapper):
    """
    Wraps a native multiline text area. If TextControlMixin works
    for your backend, you shouldn't need to change anything here.
    """
    _beos_class = BScrollView.BScrollView
    _beos_sub_class = BTextView.BTextView
    _beos_border = B_FANCY_BORDER
    _h_scroll = 0
    _v_scroll = 1
    _beos_sub = None
    
    def widgetFactory(self,*args,**kwds):
        self._beos_bounds = list(self.getGeometry())
        #self._beos_bounds[3] /= 2
        self._beos_bounds[2] *= 2.28
        self._beos_bounds = tuple(self._beos_bounds)
        self._beos_sub = self._beos_sub_class(self._beos_bounds,
                                              str(self._beos_id)+"_sub",
                                              (0.0,0.0,self._beos_bounds[2],self._beos_bounds[3]),
                                              self._beos_mode,
                                              self._beos_flags)
        self._init_args = (str(self._beos_id),
                           self._beos_sub,
                           self._beos_mode,
                           self._beos_flags,
                           self._h_scroll,
                           self._v_scroll,
                           self._beos_border)
        return ComponentWrapper.widgetFactory(self,*args,**kwds)




#==========================================================================#
# Base Class for Container Widgets

class ContainerMixin:
    """
    Frames - that is, widgets whose job is to visually group
    other widgets - often have a lot of behavior in common
    with top-level windows. Abstract that behavior here.
    """

    def setContainer(self,container):
        """
        Most backends create native widgets when the front-end
        widget is added to a container. That means that containers
        must recursively ensure that their contents are created
        when they are added to a higher-level container. For
        example, a Frame being added to a Window must ensure
        that all of its contents are created and updated to
        match the front-end state. The easiest way to handle
        that is to simply call all of the contents'
        setContainer() methods.
        """
        if self.widget is None:
            self.destroy()
        if container is None:
            #self.widget.parent = None
            return

        # Ensure this container's widget is created.
        self.create()

        # Add self to the back-end container in the proper way.  This
        # operation will be different for frames and top-level
        # windows, so we call a method to handle it.
        self.addToContainer(container)

        # Ensure geometry, etc are up to date.
        self.proxy.push(blocked=['container'])

        # Ensure all contents are created.
        for comp in self.proxy.contents:
            comp.container = self.proxy

    def getGeometry(self):
        """ Get the native widget's geometry as an (x,y,w,h) tuple.
        Since the geometry can be changed by the user dragging the
        window frame, you must implement this method. """
        if self.widget is None:
            return (self.proxy.state['x'],
                    self.proxy.state['y'],
                    self.proxy.state['width'],
                    self.proxy.state['height'])
        return self.widget.Frame()
            
    def _getContainer(self): return self.widget
    
    def setEnabled(self, enabled): pass
    
#==========================================================================#
# GroupBox

class GroupBoxWrapper(ContainerMixin, ComponentWrapper):

    _beos_class = BBox.BBox
    _beos_mode = B_FOLLOW_LEFT + B_FOLLOW_TOP
    _beos_flags = B_WILL_DRAW + B_FRAME_EVENTS + B_NAVIGABLE_JUMP
    _beos_border = B_FANCY_BORDER
    
    def widgetFactory(self, *args, **kwds):
        self._beos_bounds = self.getGeometry()
        self._init_args = (self._beos_bounds,
                           str(self._beos_id),
                           self._beos_mode,
                           self._beos_flags,
                           self._beos_border)
        return ComponentWrapper.widgetFactory(self,*args,**kwds)
    
    def addToContainer(self,container):
        if self.widget is None: return
        if container is None: return
        container.wrapper.widget.AddChild(self.widget)
    
    def setText(self, text):
        if self.widget is None: return
        self.widget.SetLabel(text)
        
    def widgetSetUp(self):
        title = self.proxy.state['text']
        #self.widget.SetLabel(title)
    
    def setupChildWidgets(self):
        for component in self.proxy.contents:
            component.container = self.proxy


#==========================================================================#
# Frame - BROKEN

class FrameWrapper(ContainerMixin,ComponentWrapper):

    _beos_class = BView.BView
    
    def widgetFactory(self,*args,**kwds):
        self._beos_bounds = self.getGeometry()
        self._init_args = (self._beos_bounds,
                           str(self._beos_id),
                           self._beos_mode,
                           self._beos_flags)
        return ComponentWrapper.widgetFactory(self,*args,**kwds)

    #def __init__(self,*args,**kws):
    #    ComponentWrapper.__init__(self,*args,**kws)

    def addToContainer(self,container):
        """
        Add the Frame to its back-end container (another
        Frame or a Window).
        """
        #container.wrapper.widget.add(self.widget)
        #print container.wrapper.widget
        #raise NotImplementedError, 'should be implemented by subclasses'
    
#==========================================================================#
# Window

class WindowWrapper(ContainerMixin,ComponentWrapper):
    """
    Wraps a top-level window frame.
    """
    
    _beos_class  = BWindow.BWindow
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
    _title = "Manygui Window"
    
    def widgetFactory(self,*args,**kwds):
        self._beos_bounds = self.getGeometry()
        if 'title' in self.proxy.state:
            self._title = self.proxy.state['title']
        self._init_args = (self._beos_bounds,
                           self._title,
                           self._beos_style,
                           self._beos_flags,
                           self._beos_workspaces)        
        return ComponentWrapper.widgetFactory(self,*args,**kwds)
        
    def setTitle(self,title):
        if self.widget is None: return
        self.widget.SetTitle(title)
    
    def setText(self,text):
        if self.widget is None: return
        pass # text is not the Title !
    
    def setEnabled(self,enabled):
        if self.widget is None: return
        self.widget.Minimize(not enabled)

    def addToContainer(self,container):
        """
        Add self to the backend application, if required.
        """
        pass
        
    def widgetSetUp(self):
        """
        Arrange for self.resize() to be called whenever the user
        interactively resizes the window.
        """
        self.widget.bind(self) # Make QuitRequested/MessageReceived work!!!

    def resize(self,dw,dh):
        """
        Inform the proxy of a resize event. The proxy then takes care of
        laying out the container contents. Don't change this method,
        just call it from an event handler.
        """
        self.proxy.resized(dw, dh)

    def setContainer(self,container):
        if not application().isRunning(): return
        if container is None: pass
        if self.widget is None: self.create(container)
        self.proxy.push(blocked=['container'])
        # Ensure contents are properly created.
        for comp in self.proxy.contents:
            comp.container = self.proxy
    
    def setGeometry(self,x,y,width,height):
        if self.widget is None: return
        self.widget.MoveTo(float(x)+10,float(y)+30)
        self.widget.ResizeTo(float(width),float(height))

    def getGeometry(self):
        """ Get the native widget's geometry as an (x,y,w,h) tuple.
        Since the geometry can be changed by the user dragging the
        window frame, you must implement this method. """
        if self.widget is None:
            return (self.proxy.state['x'],
                    self.proxy.state['y'],
                    self.proxy.state['width']+self.proxy.state['x'],
                    self.proxy.state['height']+self.proxy.state['y'])
        return self.widget.Frame()

    def setVisible(self,visible):
        """ Set/get the native widget's visibility. """
        if self.widget is None: return
        self.widget.Minimize(not visible)
        
    def destroy(self):
        self.Quit()
    
    def enterMainLoop(self):
        pass

    # BeOS Hook Functions
    
    def QuitRequested(self):
        """
        This BeOS hook function is called whenever a quit type action is requested.
        Currently sends a Quit message to the app if it is the last window.
        """
        if BApplication.be_app.CountWindows() == 1:
            BApplication.be_app.PostMessage(B_QUIT_REQUESTED)
        return 1
    
    def FrameResized(self, width, height):
        dw = width - self.proxy.state['width']
        dh = height - self.proxy.state['height']
        self.resize(dw,dh)
    
    def FrameMoved(self, origin):
        pass
        
    def MenusBeginning(self):
        pass

    def MenusEnded(self):
        pass
    
    def MessageReceived(self, msg):
        if msg.what == ACTION:
            id = msg.FindString('self_id')
            action = msg.FindString('event')
            #print id, action
            #print self.proxy.state
            for item in self.proxy.state['contents']:
                if item.wrapper._beos_id == id:
                    send(item.wrapper.proxy,action)
#==========================================================================#
# AboutDialog

ABOUT_TEXT="""
The purpose of the Manygui project is to create an easy-to-use, simple, \
and generic module for making graphical user interfaces in Python. \
Its main feature is that it works transparently with many different \
GUI packages on most platforms.
"""

class AboutDialog:
    
    def __init__(self):
        self.alert = BAlert.BAlert("About Manygui", self.ABOUT_TEXT, "OK", B_INFO_ALERT)
        self.wrapper = "AboutDialog"
    
    
    
    

#==========================================================================#
# Application

class Application(BApplication.BApplication, AbstractApplication):
    """
    Wraps a backend Application object (or implements one from
    scratch if necessary).
    """
    
    _beos_class = BApplication.BApplication # Needs to be subclassed to work!
    _beos_running = 0
    _beos_sig = "application/python"
    about = None

    def __init__(self,**kwds):
        BApplication.BApplication.__init__(self, self._beos_sig)
        AbstractApplication.__init__(self,**kwds)
        self._running = 1

    def add(self, win):
        AbstractApplication.add(self, win)
        if self._beos_running:
            if win.wrapper is "Alert":
                win.alert.Go()
            if win.wrapper.widget is None:
                win.wrapper.create()
            win.wrapper.widget.Show()
        
    def OnInit(self):
        return 1

    def internalRun(self):
        """
        Do whatever is necessary to start your backend's event-
        handling loop.
        """
        self._beos_running = 1
        BApplication.be_app.Run()

    # BeOS Hook Functions
    
    def AboutRequested(self):
        if self.about is None:
            self.about = BAlert.BAlert("About", __doc__, "Dismiss")
        self.about.Go()
        
    def ArgvRecieved(self, argc, argv):
        pass
 
    def ReadyToRun(self):
        for win in self._windows:
            if win.wrapper is "AboutDialog":
                self.about = win.alert
            else:
                win.wrapper.widget.Show()
                win.wrapper.widget.Minimize(not win.wrapper.proxy.state['visible'])

    def QuitRequested(self):
        self.about = None
        return 1
