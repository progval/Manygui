"""
skelgui.py is an empty skeleton waiting for you to implement an
Manygui back-end.

You should probably read IRFC14 (nondist/irfc/irfc-0014.txt
in the CVS repository) before trying to implement an
Manygui backend. Specifically, you should understand the
terms "proxy", "wrapper", and "(native) widget" as
they're used in Manygui. The classes implemented in
a backend (and the classes in this file) are "wrappers"
around "native widgets".

To use this skeleton, simply copy it to a file in the
manygui/lib/backends directory called <yourbackend>gui.py,
and implement all of the methods and event handlers
described below. Depending on your particular backend, there
may be some opportunities to combine methods into mixin classes.

The fastest way to resolve any questions or ambiguities
about this file, is to look at one of the existing
back-end implementations in the manygui/lib/manygui/backends
directory. Failing that, post your question to
the Manygui development list (devel@manygui.org).

If you are implementing an Manygui backend, you should
be subscribed to the development list. See

http://lists.sourceforge.net/lists/listinfo/manygui-devel

for subscription instructions.

Comments and criticism to jknapka@earthlink.net (Joe Knapka).
"""

__all__ = '''

  Application
  ButtonWrapper
  WindowWrapper
  LabelWrapper
  TextFieldWrapper
  TextAreaWrapper
  ListBoxWrapper
  RadioButtonWrapper
  CheckBoxWrapper

'''.split()

# Import Manygui infrastructure. You shouldn't have to change these.
from manygui.backends import *
from manygui.Applications import AbstractApplication
from manygui.Wrappers import AbstractWrapper
from manygui.Events import *
from manygui.Exceptions import Error
from manygui.Utils import log
from manygui import application
# End Manygui imports.

# Import anything needed to access the backend API. This is
# your job!
#...
# End backend API imports.

class ComponentWrapper(AbstractWrapper):
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
        """ Create and return the backend widget for this wrapper. For
        example, mswgui.py uses the win32gui.CreateWindowEx() call
        here to create a Windows native widget. The value returned
        will be immediately assigned to self.widget by the Manygui
        framework; henceforth you should refer to self.widget. """
        raise NotImplementedError('should be implemented by subclasses')

    def enterMainLoop(self): # ...
        """ enterMainLoop() is called when the application event loop is
        started for the first time. """
        raise NotImplementedError('should be implemented by subclasses')

    def destroy(self):
        """
        destroy() is called when the application needs to destroy the
        native widget. You can also call it within the wrapper code if
        you need to destroy your native widget for some reason. You
        should set self.widget to None here, after destroying the
        native widget.
        """
        self.widget = None
        raise NotImplementedError('should be implemented by subclasses')

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
        if not self.noWidget():
            # If the container has changed, and there's already a native
            # widget, it may be necessary to take special action here.
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
        raise NotImplementedError('should be implemented by subclasses')

    def setGeometry(self,x,y,width,height):
        """ Set the native widget's geometry. Note that we call
        self.noWidget() here to see if the wrapper has a native widget
        to manage. You should probably use this idiom at the start of
        all setter and getter methods, unless you have a very good
        reason not to. """
        if self.noWidget(): return
        raise NotImplementedError('should be implemented by subclasses')

    def getGeometry(self):
        """ Get the native widget's geometry as an (x,y,w,h) tuple.
        Since the geometry can be changed by the user dragging the
        window frame, you must implement this method. """
        if self.noWidget(): return
        raise NotImplementedError('should be implemented by subclasses')

    def setVisible(self,visible):
        """ Set/get the native widget's visibility. """
        if self.noWidget(): return
        raise NotImplementedError('should be implemented by subclasses')

    def setEnabled(self,enabled):
        """ Set/get the native widget's enabled/disabled state. """
        if self.noWidget(): return
        raise NotImplementedError('should be implemented by subclasses')

    def setText(self,text):
        """ Set/get the text associated with the widget. This might be
        window title, frame caption, label text, entry field text,
        or whatever.
        """
        if self.noWidget(): return
        raise NotImplementedError('should be implemented by subclasses')

class LabelWrapper(ComponentWrapper):
    """
    Wraps a backend "label" widget - static text.
    You may need to implement setText() here.
    """

class ListBoxWrapper(ComponentWrapper):
    """
    Wraps a backend listbox.

    At the moment, Manygui supports only single-select mode.
    """

    def setItems(self,items):
        """
        Set the contents of the listbox widget. 'items' is a list of
        strings, or of str()-able objects.
        """
        if self.noWidget(): return
        raise NotImplementedError('should be implemented by subclasses')

    def getItems(self):
        """
        Return ths listbox contents, in order, as a list of strings.
        """
        if self.noWidget(): return
        raise NotImplementedError('should be implemented by subclasses')

    def setSelection(self,selection):
        """
        Set the selection. 'selection' is an integer indicating the
        item to be selected.
        """
        if self.noWidget(): return
        raise NotImplementedError('should be implemented by subclasses')

    def getSelection(self):
        """
        Return the selected listbox item index as an integer.
        """
        if self.noWidget(): return
        raise NotImplementedError('should be implemented by subclasses')

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
        raise NotImplementedError('should be implemented by subclasses')

    def _select(self,*args):
        """
        Send an Manygui 'select' event when the user clicks or otherwise
        selects a listbox item. Note that the source of the event is
        self.proxy, not self; that's because application code only
        knows about proxies, not wrappers, so the source of the Manygui
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
        raise NotImplementedError('should be implemented by subclasses')

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
        raise NotImplementedError('should be implemented by subclasses')

    def setOn(self,on):
        """ Set the button's state. """
        if self.noWidget(): return
        raise NotImplementedError('should be implemented by subclasses')

class CheckBoxWrapper(ToggleButtonMixin):
    """
    Usually ToggleButtonMixin completely handles the CheckBox
    behavior, but in case it doesn't, you may need to write some
    code here.
    """

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

    def _click(self,*args,**kws):
        try:
            # Ensure the other buttons in the group are updated
            # properly. Note that if for some reason you need to
            # implement getValue(), this code will no longer
            # work due to the pull mechanism.
            self.proxy.group.value = self.proxy.value
        except AttributeError:
            pass
        send(self.proxy,'click')

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
        raise NotImplementedError('should be implemented by subclasses')

    def getText(self):
        """
        Fetch the widget's associated text. You *must* implement this
        to get the text from the native widget; the default getText()
        from ComponentWrapper (almost) certainly won't work.
        """
        if self.noWidget(): return
        raise NotImplementedError('should be implemented by subclasses')

    def setEditable(self,editable):
        """
        Set the editable state of the widget. If 'editable' is 0,
        the widget should allow selection and copying of its text,
        but should not accept user input.
        """
        if self.noWidget(): return
        raise NotImplementedError('should be implemented by subclasses')

    def getSelection(self):
        """
        Return the first and last+1 character indexes covered by the
        selection, as a tuple; or (0,0) if there's no selection.
        """
        if self.noWidget(): return
        raise NotImplementedError('should be implemented by subclasses')

    def setSelection(self,selection):
        """
        Select the indicated text. 'selection' is a tuple of two
        integers indicating the first and last+1 indexes within
        the widget text that should be covered by the selection.
        """
        if self.noWidget(): return
        raise NotImplementedError('should be implemented by subclasses')

class TextFieldWrapper(TextControlMixin,ComponentWrapper):
    """
    Wraps a native single-line entry field.
    """

    def widgetSetup(self):
        """
        Arrange for a press of the "Enter" key to call self._return.
        """
        raise NotImplementedError('should be implemented by subclasses')

    def _return(self,*args,**kws):
        send(self.proxy, 'enterkey')

class TextAreaWrapper(TextControlMixin,ComponentWrapper):
    """
    Wraps a native multiline text area. If TextControlMixin works
    for your backend, you shouldn't need to change anything here.
    """

# Incomplete: fix the remainder of this file!

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
        if not self.noWidget():
            self.destroy()
        if container is None:
            self.widget.parent = None
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

class FrameWrapper(ContainerMixin,ComponentWrapper):

    def __init__(self,*args,**kws):
        ComponentWrapper.__init__(self,*args,**kws)

    def addToContainer(self,container):
        """
        Add the Frame to its back-end container (another
        Frame or a Window).
        """
        #container.wrapper.widget.add(self.widget)
        raise NotImplementedError('should be implemented by subclasses')

class WindowWrapper(ContainerMixin,ComponentWrapper):
    """
    Wraps a top-level window frame.
    """

    def setTitle(self,title):
        if self.noWidget(): return
        self.widget.set_title(title)

    def addToContainer(self,container):
        """
        Add self to the backend application, if required.
        """
        raise NotImplementedError('should be implemented by subclasses')

    def widgetSetUp(self):
        """
        Arrange for self.resize() to be called whenever the user
        interactively resizes the window.
        """
        raise NotImplementedError('should be implemented by subclasses')

    def resize(self,dw,dh):
        """
        Inform the proxy of a resize event. The proxy then takes care of
        laying out the container contents. Don't change this method,
        just call it from an event handler.
        """
        self.proxy.resized(dw, dh)

class Application(AbstractApplication):
    """
    Wraps a backend Application object (or implements one from
    scratch if necessary).

    wxgui's Application class inherits wxPython's Application class.
    On the other hand, Tk has no Application class, so tkgui's
    Application class simply calls Tk.mainloop() in its
    Application.internalRun() method.
    """

    def internalRun(self):
        """
        Do whatever is necessary to start your backend's event-
        handling loop.
        """
        raise NotImplementedError('should be implemented by subclasses')
