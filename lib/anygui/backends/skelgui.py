"""
skelgui.py is an empty skeleton waiting for you to implement an
Anygui back-end. Simply implement all of the methods documented
below. Depending on your particular backend, there may be
some opportunities to combine methods into mixin classes.

To use this skeleton, simply copy it to a file in the
anygui/lib/backends directory called <yourbackend>gui.py,
and implement all of the methods and event handlers
described below.
"""

# Import Anygui infrastructure. You shouldn't have to change these.
from anygui.backends import *
from anygui.Applications import AbstractApplication
from anygui.Wrappers import AbstractWrapper, DummyWidget, isDummy
from anygui.Events import *
from anygui.Exceptions import Error
from anygui.Utils import log
from anygui import application
# End Anygui imports.

# Import anything needed to access the backend API. This is
# your job!
#...
# End backend API imports.

class ComponentWrapper(AbstractWrapper):
    """
    The ComponentWrapper class should abstract away all behavior
    that all backend widgets perform similarly. Normally, this
    will include geometry and visibility management, and in some
    cases widget creation can be handled here as well (see
    mswgui.py for example).
    """

    def __init__(self, *args, **kwds):
        """
        Common widget wrapper initialization code. The main thing that
        we would normall do here is set any backend-specific
        attribute constraints.
        
        Whenever the application code alters a widget, the front end
        will "push" any changed widget attributes into the backend by
        calling the set<Attribute>(self,new_value) method for any
        attributes that changes. The setContraints() method allows the
        backend to specify the order in which the set<Attribute>()
        method calls are made, by specifying the order in which attribute
        names are set. The constraints set here are just examples.
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
        """ Create and return the backend widget for this wrapper. For
        example, mswgui.py uses the win32gui.CreateWindowEx() call
        here to create a Windows native widget. The value returned
        will be immediately assigned to self.widget by the Anygui
        framework; henceforth you should refer to self.widget. """
        raise NotImplementedError, 'should be implemented by subclasses'

    def enterMainLoop(self): # ...
        """ enterMainLoop() is called when the application event loop is
        started for the first time. """
        raise NotImplementedError, 'should be implemented by subclasses'

    def destroy(self):
        """
        destroy() is called when the application needs to destroy the
        native widget. You can also call it within the wrapper code if
        you need to destroy your native widget for some reason. You
        should set self.widget to DummyWidget()
        here, after destroying the native widget.
        """
        self.widget = DummyWidget()
        raise NotImplementedError, 'should be implemented by subclasses'

    # From here on, all methods in this class are getters and setters.
    # Setters must be implemented; they are called automatically in
    # response to application-code manipulation of the associated
    # proxy object, and perform the required magic on self.widget
    # to implement the change.
    #
    # Getters need not be implemented unless the backend requires
    # special handling, or if the attribute in question can be changed
    # by user actions as well as by application code. Getters are
    # called automatically by proxy attribute access, if they
    # exist; otherwise the last value set in the proxy is returned.
    # Note that if you elect not to implement a getter, *you*
    # *must* *remove* *the* *empty* *getter* *def* from this
    # class.
    #
    # The setters and getters here are a typlical example of
    # attribute handling that's common to all of a backend's
    # widgets. For example, getGeometry() and setGeometry() work
    # the same for any backend widget, thus they're included
    # here in the common wrapper base class.

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

        When the widget is removed from it's container, setContainer()
        will be called with container==None; you must handle that case
        correctly, whatever that means for your backend.
        """
        if not self.noWidget():
            # If the container has changed, and there's already a native
            widget, it may be necessary to take special action here.
            pass
        if container is None:
            # Handle "removed from container" case.
            return
        self.create()

        # Be sure to handle any backend container/contents protocol
        # here!
        # ...

        # Ensure native widget is brought up to date wrt the proxy
        # state.
        self.proxy.push(blocked=['container'])
        raise NotImplementedError, 'should be implemented by subclasses'

    def setGeometry(self,x,y,width,height):
        """ Set/get the native widget's geometry. Note that we call
        self.noWidget() here to see if the wrapper has a native widget
        to manage. You should probably use this idiom at the start of
        all setter and getter methods, unless you have a very good
        reason not to. """
        if self.noWidget(): return
        raise NotImplementedError, 'should be implemented by subclasses'
    def getGeometry(self):
        """ Set/get the native widget's geometry as an (x,y,w,h) tuple.
        Since the geometry can be changed by the user dragging the
        window frame, you must implement this method. """
        if self.noWidget(): return
        raise NotImplementedError, 'should be implemented by subclasses'

    def setVisible(self,visible):
        """ Set/get the native widget's visibility. """
        if self.noWidget(): return
        raise NotImplementedError, 'should be implemented by subclasses'
    def getVisible(self):
        if self.noWidget(): return
        raise NotImplementedError, 'should be implemented by subclasses'

    def setEnabled(self,enabled):
        """ Set/get the native widget's enabled/disabled state. """
        if self.noWidget(): return
        raise NotImplementedError, 'should be implemented by subclasses'    def setEnabled(self,enabled):
    def getEnabled(self):
        if self.noWidget(): return
        raise NotImplementedError, 'should be implemented by subclasses'

    def setText(self,text):
        """ Set/get the text associated with the widget. This might be
        window title, frame caption, label text, entry field text,
        or whatever.
        """
        if self.noWidget(): return
        raise NotImplementedError, 'should be implemented by subclasses'
    def getText(self):
        """
        Fetch the widget's associated text. You normally don't need to
        implement this except for TextField and TextArea controls.
        """
        if self.noWidget(): return
        raise NotImplementedError, 'should be implemented by subclasses'


class LabelWrapper(ComponentWrapper):
    """
    Wraps a backend "label" widget - static text.
    You may need to implement setText() here.
    """

class ListBoxWrapper(ComponentWrapper):
    """
    Wraps a backend listbox.

    At the moment, Anygui supports only single-select mode.
    """

    def setItems(self,items):
        """
        Set the contents of the listbox widget. 'items' is a list of
        strings, or of str()-able objects.
        """
        if self.noWidget(): return
        raise NotImplementedError, 'should be implemented by subclasses'

    def getItems(self):
        """
        Return ths listbox contents, in order, as a list of strings.
        """
        if self.noWidget(): return
        raise NotImplementedError, 'should be implemented by subclasses'

    def setSelection(self,selection):
        """
        Set the selection. 'selection' is an integer indicating the
        item to be selected.
        """
        if self.noWidget(): return
        raise NotImplementedError, 'should be implemented by subclasses'

    def getSelection(self):
        """
        Return the selected listbox item index as an integer.
        """
        if self.noWidget(): return
        raise NotImplementedError, 'should be implemented by subclasses'

    def widgetSetUp(self):
        """
        widgetSetUp() is called by the Anygui framework immediately after
        the native widget has been created and assigned to self.widget.
        The most common use of widgetSetUp() is to register any event
        handlers necessary to deal with user actions.

        The ListBox widget requires that an Anygui 'select' event be
        fired whenever the user selects an item of the listbox.
        self._select() sends the event, so here you should associate
        the back-end's selection event with the self._select method.
        """
        raise NotImplementedError, 'should be implemented by subclasses'

    def _select(self,*args):
        """
        Send an Anygui 'select' event when the user clicks or otherwise
        selects a listbox item. Note that the source of the event is
        self.proxy, not self; that's because application code only
        knows about proxies, not wrappers, so the source of the Anygui
        event must be a proxy.
        """
        send(self.proxy,'select')

#class CanvasWrapper(ComponentWrapper):
# Fix me!
#    _twclass = tw.Canvas

class ButtonWrapper(ComponentWrapper):
    """
    Wraps a backend command-button widget - the kind you click
    on to initiate an action, eg "OK", "Cancel", etc.
    """

    def widgetSetUp(self):
        """
        Register a backend event handler to call self.click when
        the user clicks the button.
        """
        raise NotImplementedError, 'should be implemented by subclasses'

    def _click(self,*args,**kws):
        send(self.proxy,'click')


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
        if self.noWidget(): return
        raise NotImplementedError, 'should be implemented by subclasses'

    def setOn(self,on):
        if self.noWidget(): return
        raise NotImplementedError, 'should be implemented by subclasses'

class CheckBoxWrapper(ToggleButtonMixin):
    """
    Usually ToggleButtonMixin completely handles the CheckBox
    behavior, but in case it doesn't, you may need to write some
    code here.
    """

class RadioButtonWrapper(ToggleButtonMixin):
    """
    Radio buttons are a pain. Only one member of an RB "group" may be
    active at a time. Anygui provides the RadioGroup front-end
    class, which takes care of querying the state of radiobuttons
    and setting their state in a mutually exclusive manner.
    However, many backends also enforce this mutual exclusion,
    which means that things can get complicated. The RadioGroup
    class is implemented in as non-intrusive a way as possible,
    but it can be a challenge to arrange for them to act in
    the correct way, backend-wise. Look at the other backend
    implementations for some clues.

    In the case where a backend implements radiobuttons as
    a simple visual variant of checkboxes with no mutual-exclusion
    behavior, the ToggleButtonMixin class already does everything
    you need; just create the proper backend widget in
    RadioButtonWrapper.widgetFactory(). You can usually fake
    that kind of backend implementation by playing tricks
    with the backend's mutual-exclusion mechanism. For example,
    create a tiny frame to encapsulate the backend radiobutton,
    if your backend enforces mutual exclusion on a
    per-frame basis.
    """

class TextControlMixin:
    """
    Single-line entry fields and multiline text controls usually
    have a lot of common behavior that can be abstracted away. Do
    that here.
    """

    def setText(self,text):
        """ Set/get the text associated with the widget. This might be
        window title, frame caption, label text, entry field text,
        or whatever.
        """
        if self.noWidget(): return
        raise NotImplementedError, 'should be implemented by subclasses'

    def getText(self):
        """
        Fetch the widget's associated text. You *must* implement this
        to get the text from the native widget; the default getText()
        from ComponentWrapper (almost) certainly won't work.
        """
        if self.noWidget(): return
        raise NotImplementedError, 'should be implemented by subclasses'

    def setEditable(self,editable):
        """
        Set the editable state of the widget. If 'editable' is 0,
        the widget should allow selection and copying of its text,
        but should not accept user input.
        """
        if self.noWidget(): return
        raise NotImplementedError, 'should be implemented by subclasses'

    def getSelection(self):
        """
        Return the first and last+1 character indexes covered by the
        selection, as a tuple; or (0,0) if there's no selection.
        """
        if self.noWidget(): return
        raise NotImplementedError, 'should be implemented by subclasses'

    def setSelection(self,selection):
        """
        Select the indicated text. 'selection' is a tuple of two
        integers indicating the first and last+1 indexes within
        the widget text that should be covered by the selection.
        """
        if self.noWidget(): return
        raise NotImplementedError, 'should be implemented by subclasses'

class TextFieldWrapper(TextControlMixin,ComponentWrapper):
    """
    Wraps a native single-line entry field.
    """

    def widgetSetup(self):
        """
        Arrange for a press of the "Enter" key to call self._return.
        """
        raise NotImplementedError, 'should be implemented by subclasses'

    def _return(self,*args,**kws):
        send(self.proxy, 'enterkey')

class TextAreaWrapper(TextControlMixin,ComponentWrapper):
    """
    Wraps a native multiline text area. If TextControlMixin works
    for your backend, you shouldn't need to change anything here.
    """

# Incomplete: fix the remainder of this file!

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
