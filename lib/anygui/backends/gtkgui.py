
from anygui.backends import *
__all__ = anygui.__all__

################################################################

from gtk import *
import gtk

class ComponentMixin:
    _gtk_comp = None
    _gtk_id = None
    _gtk_style = 0
    _connected = 0
    
    def _is_created(self):
        return self._gtk_comp is not None

    def _ensure_created(self):
        if self._gtk_comp is None:
            self._gtk_comp = self._gtk_class(*self._init_args)
            self._ensure_visibility()
            self._ensure_events()
            self._ensure_geometry()
            self._ensure_enabled_state()
            if self._container is not None:
                self._container._gtk_add(self)
            return 1
        return 0

    def _ensure_events(self):
        pass

    def _ensure_geometry(self):
        if self._gtk_comp:
            self._gtk_comp.set_uposition(int(self._x), int(self._y))
            self._gtk_comp.set_usize(int(self._width), int(self._height))

    def _ensure_visibility(self):
        if self._gtk_comp:
            if self._visible:
                self._gtk_comp.show()
            else:
                self._gtk_comp.hide()

    def _ensure_enabled_state(self):
        if self._gtk_comp:
            self._gtk_comp.set_sensitive(int(self._enabled))

    def _ensure_destroyed(self):
        if self._gtk_comp:
            self._gtk_comp.destroy()
            self._gtk_comp = None
            self._connected = 0

    def _get_gtk_text(self):
        return str(self._text)

    def _ensure_text(self):
        pass

################################################################

class Label(ComponentMixin, AbstractLabel):
    _gtk_class = GtkLabel

    def _ensure_created(self):
        self._init_args = (str(self._text),)
        return ComponentMixin._ensure_created(self)

    def _ensure_text(self):
        if self._gtk_comp:
            self._gtk_comp.set_text(str(self._text))

################################################################

class Button(ComponentMixin, AbstractButton):
    _gtk_class = GtkButton

    def _ensure_created(self):
        self._init_args = (str(self._text),)
        ret = ComponentMixin._ensure_created(self)
        return ret

    def _ensure_events(self):
        if self._gtk_comp and not self._connected:
            self._gtk_comp.connect("clicked", self._gtk_clicked)
            self._connected = 1

    def _ensure_text(self):
        if self._gtk_comp:
            self._gtk_comp.children()[0].set_text(str(self._text))

    def _gtk_clicked(self, *args):
        send(self, 'click')

class ToggleButtonMixin(ComponentMixin):
    def _ensure_state(self):
        if self._gtk_comp:
            self._gtk_comp.set_active(int(self._on))

    def _ensure_events(self):
        if self._gtk_comp and not self._connected:
            self._gtk_comp.connect("toggled", self._gtk_toggled)
            self._connected = 1

    def _gtk_toggled(self, *args):
        val = self._gtk_comp.get_active()
        if val == int(self._on):
            return
        self.modify(on=val)
        #self.do_action()
        send(self, 'click')

    def _ensure_text(self):
        if self._gtk_comp:
            self._gtk_comp.children()[0].set_text(str(self._text))

class CheckBox(ToggleButtonMixin, AbstractCheckBox):
    _gtk_class = GtkCheckButton

    def _ensure_created(self):
        self._init_args = (str(self._text),)
        return ComponentMixin._ensure_created(self)

class RadioButton(ToggleButtonMixin, AbstractRadioButton):
    _gtk_class = GtkRadioButton

    def _ensure_created(self):
        if self._group and len(self._group._items) > 1:
            for item in self._group._items:
                if item is not self:
                    break
            else:
                raise InternalError(self, "Couldn't find non-self group item!")
            self._init_args = (item._gtk_comp, str(self._text))
        else:
            self._init_args = (None, str(self._text))
        return ComponentMixin._ensure_created(self)

    def _gtk_toggled(self, *args):
        val = self._gtk_comp.get_active()
        if val == int(self._on):
            return
        self.modify(on=val)
        if int(self._on):
            if self.group is not None:
                self.group.modify(value=self.value)
            send(self, 'click')

################################################################

class ScrollableListBox(GtkScrolledWindow):
    def __init__(self, *args, **kw):
        GtkScrolledWindow.__init__(self, *args, **kw)
        self._listbox = GtkCList()
        self._listbox.show()
        self.set_policy(POLICY_AUTOMATIC, POLICY_AUTOMATIC)
        self.add_with_viewport(self._listbox)

class ListBox(ComponentMixin, AbstractListBox):
    _gtk_class = ScrollableListBox

    def _ensure_created(self):
        self._init_args = ()
        return ComponentMixin._ensure_created(self)

    def _backend_selection(self):
        if self._gtk_comp:
            return self._gtk_comp._listbox.selection[0]

    def _ensure_items(self):
        if self._gtk_comp:
            self._gtk_comp._listbox.clear()
            for item in self._items:
                self._gtk_comp._listbox.append([item])

    def _ensure_events(self):
        if self._gtk_comp and not self._connected:
            self._gtk_comp._listbox.connect("select_row", self._row_selected)
            self._connected = 1

    def _row_selected(self, *args):
        #self.do_action()
        send(self, 'select')

    def _ensure_selection(self):
        pass

################################################################

class TextField(ComponentMixin, AbstractTextField):
    _gtk_class = GtkEntry
    _ignore_changed = 0

    def _ensure_created(self):
        self._init_args = ()
        return ComponentMixin._ensure_created(self)

    def _ensure_text(self):
        if self._gtk_comp:
            self._ignore_changed = 1
            self._gtk_comp.set_text(str(self._text))
            self._ignore_changed = 0

    def _ensure_selection(self):
        if self._gtk_comp:
            start, end = self._selection
            self._gtk_comp.select_region(start, end)

    def _ensure_editable(self):
        if self._gtk_comp:
            self._gtk_comp.set_editable(int(self._editable))

    def _ensure_events(self):
        if self._gtk_comp and not self._connected:
            self._gtk_comp.connect("activate", self._entry_activated)
            # XXX, currently updates on any change in the textfield.
            # Perhaps too CPU intensive?
            self._gtk_comp.connect("changed", self._entry_changed)
            self._connected = 1

    def _backend_selection(self):
        if self._gtk_comp:
            start, end = int(self._gtk_comp.selection_start_pos), \
                        int(self._gtk_comp.selection_end_pos)
            if start > end:
                return end, start
            else:
                return start, end

    def _backend_text(self):
        if self._gtk_comp:
            return str(self._gtk_comp.get_text())

    def _entry_activated(self, *args):
        #self.do_action()
        send(self, 'enterkey')

    def _entry_changed(self, *args):
        if not self._ignore_changed:
            self.modify(text=self._backend_text())

class ScrollableTextArea(GtkScrolledWindow):
    def __init__(self, *args, **kw):
        GtkScrolledWindow.__init__(self, *args, **kw)
        self._textarea = GtkText()
        self._textarea.show()
        self.set_policy(POLICY_AUTOMATIC, POLICY_AUTOMATIC)
        self.add_with_viewport(self._textarea)

class TextArea(ComponentMixin, AbstractTextArea):
    _gtk_class = ScrollableTextArea
    _connected = 0
    _ignore_changed = 0

    def _ensure_created(self):
        self._init_args = ()
        return ComponentMixin._ensure_created(self)

    def _ensure_text(self):
        if self._gtk_comp:
            if str(self._text) != self._backend_text():
                self._ignore_changed = 1
                p = self._gtk_comp._textarea.get_point()
                self._gtk_comp._textarea.freeze()
                self._gtk_comp._textarea.set_point(0)
                self._gtk_comp._textarea.delete_text(0, -1)
                self._gtk_comp._textarea.insert_defaults(str(self._text))
                self._gtk_comp._textarea.set_point(p)
                self._gtk_comp._textarea.thaw()
                self._ignore_changed = 0

    def _ensure_editable(self):
        if self._gtk_comp:
            self._gtk_comp._textarea.set_editable(int(self._editable))

    def _ensure_selection(self):
        if self._gtk_comp:
            start, end = self._selection
            self._gtk_comp._textarea.select_region(start, end)

    def _ensure_events(self):
        if self._gtk_comp and not self._connected:
            # XXX, currently updates on any change in the textfield.
            # Perhaps too CPU intensive?
            self._gtk_comp._textarea.connect("changed", self._text_changed)
            self._connected = 1

    def _backend_selection(self):
        if self._gtk_comp:
            start, end = int(self._gtk_comp._textarea.selection_start_pos), \
                        int(self._gtk_comp._textarea.selection_end_pos)
            if start > end:
                return end, start
            else:
                return start, end

    def _backend_text(self):
        if self._gtk_comp:
            end = self._gtk_comp._textarea.get_length()
            return str(self._gtk_comp._textarea.get_chars(0, end))

    def _text_changed(self, *args):
        if not self._ignore_changed:
            self.modify(text=self._backend_text())

################################################################

class Frame(ComponentMixin, AbstractFrame):
    _gtk_class = GtkLayout
    _visible = 0
    _init_args = ()

    def _gtk_add(self, comp):
        self._gtk_comp.put(comp._gtk_comp, int(comp._x), int(comp._y))

################################################################

class Window(ComponentMixin, AbstractWindow):
    _gtk_class = GtkWindow
    _gtk_style = 0

    def _ensure_created(self):
        if self._gtk_comp is None:
            self._gtk_comp = self._gtk_class(WINDOW_TOPLEVEL)
            self._gtk_container = GtkLayout()
            self._gtk_comp.add(self._gtk_container)
            self._gtk_container.show()
            return 1
        return 0

    def _ensure_events(self):
        self._gtk_comp.connect('destroy', self._gtk_close_handler)

    def _ensure_title(self):
        if self._gtk_comp:
            self._gtk_comp.set_title(str(self._title))

    def _gtk_close_handler(self, *args):
        global _app
        self._gtk_comp.destroy()
        self.destroy()
        _app._window_deleted()
    
    def _gtk_resize_handler(self, *args):
        w = self._qt_comp.width()
        h = self._qt_comp.height()
        dw = w - self._width
        dh = h - self._height
        #self.modify(width=w, height=h)
        self._width = w
        self._height = h
        self.resized(dw, dh)

    def _get_gtk_text(self):
        return str(self._title)

    def _gtk_add(self, comp):
        self._gtk_container.put(comp._gtk_comp, int(comp._x), int(comp._y))

################################################################

class Application(AbstractApplication):
    def __init__(self):
        AbstractApplication.__init__(self)
        global _app
        _app = self

    def _window_deleted(self):
        if not self._windows:
            mainquit()
    
    def _mainloop(self):
        mainloop()

################################################################
# Local Variables:
# compile-command: "pychecker -s gtkgui.py"
# End:
