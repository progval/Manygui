try:
    # Import Anygui infrastructure. You shouldn't have to change these.
    from anygui.backends import *
    from anygui.Applications import AbstractApplication
    from anygui.Wrappers import AbstractWrapper
    from anygui.Events import *
    from anygui import application
    # End Anygui imports.

    # Import anything needed to access the backend API. This is
    # your job!
    from gtk import *
    import gtk
    # End backend API imports.
except:
    import traceback
    traceback.print_exc()

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
  MenuWrapper
  MenuCommandWrapper
  MenuCheckWrapper
  MenuSeparatorWrapper
  MenuBarWrapper

'''.split()

class ComponentWrapper(AbstractWrapper):

    def __init__(self, *args, **kwds):

        AbstractWrapper.__init__(self, *args, **kwds)

        # 'container' before everything, then geometry.
        self.setConstraints('container','x','y','width','height')

        # addConstraint(self,before,after) adds a constraint that attribute
        # 'before' must be set before 'after', when both appear in the
        # same push operation. An attempt to set mutually contradictory
        # constraints will result in an exception.
        self.addConstraint('geometry', 'visible')

    def widgetFactory(self,*args,**kws):
        raise NotImplementedError, 'should be implemented by subclasses'

    def enterMainLoop(self): # ...
        if not self.widget: return
        self.widget.show()

    def destroy(self):
        if self.widget:
            self.widget.destroy()
        self.widget = None

    # getters and setters
    def setContainer(self,container):
        if container is None:
            self.destroy()
            return
        parent = container.wrapper.widget
        if parent is None:
            self.create(parent)
            self.proxy.push(blocked=['container'])
            self.setupChildWidgets()

    def setGeometry(self,x,y,width,height):
        if not self.widget: return
        self.widget.set_uposition(int(x), int(y))
        self.widget.set_usize(int(width), int(height))

    def getGeometry(self):
        if not self.widget: return
        return self.widget.get_uposition(int(x), int(y)) + \
               self.widget.get_usize(int(width), int(height))

    def setVisible(self,visible):
        if not self.widget: return
        if visible:
            self.widget.show()
        else:
            self.widget.hide()

    def setEnabled(self,enabled):
        if not self.widget: return
        self.widget.set_sensitive(int(enabled))

    def setText(self,text):
        if not self.widget: return
        raise NotImplementedError, 'should be implemented by subclasses'

class LabelWrapper(ComponentWrapper):

    def widgetFactory(self, *args, **kws):
        print "In LabelWrapper.widgetFactory()"
        return GtkLabel(*args, **kws)

    def setText(self, text):
        if not self.widget: return
        self.widget.set_text(str(text))

class ScrollableListBox(GtkScrolledWindow):
    """
    A scrollable list box.  Used by ListBoxWrapper.
    """
    def __init__(self, *args, **kw):
        GtkScrolledWindow.__init__(self, *args, **kw)
        self._listbox = GtkCList()
        self._listbox.show()
        self.set_policy(POLICY_AUTOMATIC, POLICY_AUTOMATIC)
        self.add_with_viewport(self._listbox)

class ListBoxWrapper(ComponentWrapper):

    connected = 0

    def widgetFactory(self, *args, **kws):
        return ScrollableListBox()

    def setItems(self,items):
        """
        Set the contents of the listbox widget. 'items' is a list of
        strings, or of str()-able objects.
        """
        if not self.widget: return
        self.widget._listbox.clear()
        for item in items:
            self.widget._listbox.append([str(item)])

    def getItems(self):
        """
        Return ths listbox contents, in order, as a list of strings.
        """
        if not self.widget: return
        return list(self.widget._listbox.rows)

    def setSelection(self,selection):
        """
        Set the selection. 'selection' is an integer indicating the
        item to be selected.
        """
        if not self.widget: return
        self.widget._listbox.select_row(int(selection), 0)

    def getSelection(self):
        """
        Return the selected listbox item index as an integer.
        """
        if not self.widget: return
        return int(self.widget._listbox.selection[0])

    def widgetSetUp(self):
        """ Connect ListBox events """
        if not self.connected:
            self.widget._listbox.connect("select_row", self._select)
            self.connected = 1

    def _select(self,*args):
        send(self.proxy,'select')

#class CanvasWrapper(ComponentWrapper):
# Fix me!
#    _twclass = tw.Canvas

class ButtonWrapper(ComponentWrapper):
    """
    Wraps a backend command-button widget - the kind you click
    on to initiate an action, eg "OK", "Cancel", etc.
    """
    connected = 0

    def widgetFactory(self, *args, **kws):
        return GtkButton(*args, **kws)

    def widgetSetUp(self):
        """
        Register a backend event handler to call self.click when
        the user clicks the button.
        """
        if not self.connected:
            self.widget.connect("clicked", self._click)
            self.connected = 1

    def setText(self, text):
        if not self.widget: return
        self.widget.children()[0].set_text(str(text))

    def _click(self,*args,**kws):
        send(self.proxy,'click')


class ToggleButtonMixin(ButtonWrapper):

    def getOn(self):
        """ Return the button's state: 1 for checked, 0 for not. """
        if not self.widget: return
        return self.widget.get_active()

    def setOn(self,on):
        """ Set the button's state. """
        if not self.widget: return
        val = self.widget.get_active()
        if val == int(on):
            return
        self.widget.set_active(int(on))

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

    In the case where a backend implements radiobuttons as a simple
    visual variant of checkboxes with no mutual-exclusion behavior,
    this class already does everything you need; just create the
    proper backend widget in RadioButtonWrapper.widgetFactory(). You
    can usually fake that kind of backend implementation by playing
    tricks with the backend's mutual-exclusion mechanism. For example,
    create a tiny frame to encapsulate the backend radiobutton, if
    your backend enforces mutual exclusion on a per-frame basis.
    """

    def widgetFactory(self, *args, **kws):
        if self.proxy.group and len(self.proxy.group._items) > 1:
            for item in self.proxy.group._items:
                if item is not self:
                    break
            else:
                raise InternalError(self, "Couldn't find non-self group item!")
            return GtkRadioButton(item.widget, *args, **kws)
        else:
            return GtkRadioButton(None, *args, **kws)

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

    def setText(self,text):
        """ Set/get the text associated with the widget. This might be
        window title, frame caption, label text, entry field text,
        or whatever.
        """
        if not self.widget: return
        raise NotImplementedError, 'should be implemented by subclasses'

    def getText(self):
        """
        Fetch the widget's associated text. You *must* implement this
        to get the text from the native widget; the default getText()
        from ComponentWrapper (almost) certainly won't work.
        """
        if not self.widget: return
        raise NotImplementedError, 'should be implemented by subclasses'

    def setEditable(self,editable):
        """
        Set the editable state of the widget. If 'editable' is 0,
        the widget should allow selection and copying of its text,
        but should not accept user input.
        """
        if not self.widget: return
        raise NotImplementedError, 'should be implemented by subclasses'

    def getSelection(self):
        """
        Return the first and last+1 character indexes covered by the
        selection, as a tuple; or (0,0) if there's no selection.
        """
        if not self.widget: return
        raise NotImplementedError, 'should be implemented by subclasses'

    def setSelection(self,selection):
        """
        Select the indicated text. 'selection' is a tuple of two
        integers indicating the first and last+1 indexes within
        the widget text that should be covered by the selection.
        """
        if not self.widget: return
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
    """
    Frames - that is, widgets whose job is to visually group
    other widgets - often have a lot of behavior in common
    with top-level windows. Abstract that behavior here.
    """
    pass

class FrameWrapper(ContainerMixin,ComponentWrapper):

    def __init__(self,*args,**kws):
        ComponentWrapper.__init__(self,*args,**kws)

    def addToContainer(self,container):
        """
        Add the Frame to its back-end container (another
        Frame or a Window).
        """
        #container.wrapper.widget.add(self.widget)
        raise NotImplementedError, 'should be implemented by subclasses'

class WindowWrapper(ContainerMixin,ComponentWrapper):
    """
    Wraps a top-level window frame.
    """
    connected = 0

    def widgetFactory(self, *args, **kws):
        print "In WindowWrapper.widgetFactory()"
        return GtkWindow(WINDOW_TOPLEVEL)

    def setTitle(self,title):
        if not self.widget: return
        self.widget.set_title(str(title))

    def addToContainer(self,container):
        """
        Add self to the backend application, if required.
        """
        raise NotImplementedError, 'should be implemented by subclasses'

    def widgetSetUp(self):
        """
        Arrange for self.resize() to be called whenever the user
        interactively resizes the window.
        """
        self._gtk_container = GtkLayout()
        self.widget.add(self._gtk_container)
        self._gtk_container.show()
        if not self.connected:
            self.widget.connect('size_allocate', self.resize)
            self.connected = 1

    def resize(self,dw,dh):
        """
        Inform the proxy of a resize event. The proxy then takes care of
        laying out the container contents. Don't change this method,
        just call it from an event handler.
        """
        self.proxy.resized(dw, dh)

class MenuWrapper:
    pass

class MenuCommandWrapper:
    pass

class MenuCheckWrapper:
    pass

class MenuSeparatorWrapper:
    pass

class MenuBarWrapper:
    pass

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
        mainloop()
