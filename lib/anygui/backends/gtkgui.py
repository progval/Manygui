
from anygui.backends import *
__all__ = anygui.__all__

################################################################

from gtk import *
import gtk

class ComponentMixin:
    # mixin class, implementing the backend methods
    # FIXME: Defaults...
    _height = -1
    _width = -1
    _x = -1
    _y = -1

    _gtk_comp = None
    _gtk_id = None
    _gtk_style = 0
    
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
            self._gtk_comp.set_uposition(self._x, self._y)
            self._gtk_comp.set_usize(self._width, self._height)

    def _ensure_visibility(self):
        if self._gtk_comp:
            if self._visible:
                self._gtk_comp.show()
            else:
                self._gtk_comp.hide()

    def _ensure_enabled_state(self):
        if self._gtk_comp:
            self._gtk_comp.set_sensitive(self._enabled)

    def _ensure_destroyed(self):
        if self._gtk_comp:
            self._gtk_comp.destroy()
            self._gtk_comp = None

    def _get_gtk_text(self):
        # helper function for creation
        # returns the text required for creation.
        # This may be the _text property, or _title, ...,
        # depending on the subclass
        return self._text

    def _ensure_text(self):
        pass

################################################################

class Label(ComponentMixin, AbstractLabel):
    _width = 100 # auto ?
    _height = 32 # auto ?
    _gtk_class = GtkLabel
    _text = "GtkLabel"

    def _ensure_created(self):
        self._init_args = (self._text,)
        return ComponentMixin._ensure_created(self)

    def _ensure_text(self):
        if self._gtk_comp:
            self._gtk_comp.set_text(self._text)

################################################################

class Button(ComponentMixin, AbstractButton):
    _gtk_class = GtkButton
    _text = "GtkButton"
    _event_connected = 0

    def _ensure_created(self):
        self._init_args = (self._text,)
        return ComponentMixin._ensure_created(self)

    def _ensure_events(self):
        if self._gtk_comp and not self._event_connected:
            self._gtk_comp.connect("clicked", self._gtk_clicked)
            self._event_connected = 1

    def _gtk_clicked(self, *args):
        self.do_action()

class ToggleButtonMixin(ComponentMixin):
    def _ensure_state(self):
        if self._gtk_comp:
            self._gtk_comp.set_active(self._on)

    def _gtk_toggled(self, *args):
        val = self._gtk_comp.get_active()
        if val == self._on:
            return
        self.model.value = val
        self.do_action()

class CheckBox(ToggleButtonMixin, AbstractCheckBox):
    _gtk_class = GtkCheckButton
    _text = "GtkCheckBox"
    _event_connected = 0

    def _ensure_created(self):
        self._init_args = (self._text,)
        return ComponentMixin._ensure_created(self)

    def _ensure_events(self):
        if self._gtk_comp and not self._event_connected:
            self._gtk_comp.connect("toggled", self._gtk_toggled)
            self._event_connected = 1

class RadioButton(ToggleButtonMixin, AbstractRadioButton):
    _gtk_class = GtkRadioButton
    _text = "GtkRadioButton"
    _event_connected = 0

    def _ensure_created(self):
        if self._group and len(self._group._items) > 1:
            for item in self._group._items:
                if item is not self:
                    break
            else:
                raise InternalError(self, "Couldn't find non-self group item!")
            self._init_args = (item._gtk_comp, self._text)
        else:
            self._init_args = (None, self._text)
        return ComponentMixin._ensure_created(self)

    def _ensure_events(self):
        if self._gtk_comp and not self._event_connected:
            self._gtk_comp.connect("toggled", self._gtk_toggled)
            self._event_connected = 1

    def _gtk_toggled(self, *args):
        val = self._gtk_comp.get_active()
        if val == self._on:
            return
        self._on = val
        if self._on:
            # XXX: Hack!
            self.do_action()

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
    _event_connected = 0

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
        if self._gtk_comp and not self._event_connected:
            self._gtk_comp._listbox.connect("select_row", self._row_selected)
            self._event_connected = 1

    def _row_selected(self, *args):
        self.do_action()

    def _ensure_selection(self):
        pass

################################################################

class TextField(ComponentMixin, AbstractTextField):
    _gtk_class = GtkEntry
    _event_connected = 0

    def _ensure_created(self):
        self._init_args = ()
        return ComponentMixin._ensure_created(self)

    def _ensure_text(self):
        if self._gtk_comp:
            self._gtk_comp.set_text(self._text)

    def _ensure_selection(self):
        if self._gtk_comp:
            start, end = self._selection
            self._gtk_comp.select_region(start, end)

    def _ensure_editable(self):
        if self._gtk_comp:
            self._gtk_comp.set_editable(self._editable)

    def _ensure_events(self):
        if self._gtk_comp and not self._event_connected:
            self._gtk_comp.connect("activate", self._entry_activated)
            self._event_connected = 1

    def _backend_selection(self):
        if self._gtk_comp:
            start, end = self._gtk_comp.selection_start_pos, \
                        self._gtk_comp.selection_end_pos
            if start > end:
                return end, start
            else:
                return start, end

    def _backend_text(self):
        if self._gtk_comp:
            return self._gtk_comp.get_text()

    def _entry_activated(self, *args):
        self.do_action()

class TextArea(ComponentMixin, AbstractTextArea):
    _gtk_class = GtkText
    _event_connected = 0

    def _ensure_created(self):
        self._init_args = ()
        return ComponentMixin._ensure_created(self)

    def _ensure_text(self):
        if self._gtk_comp:
            end = self._gtk_comp.get_length()
            point = self._gtk_comp.get_point()
            self._gtk_comp.freeze()
            self._gtk_comp.set_point(0)
            self._gtk_comp.forward_delete(end)
            self._gtk_comp.insert_defaults(self._text)
            self._gtk_comp.set_point(point)
            self._gtk_comp.thaw()

    def _ensure_editable(self):
        if self._gtk_comp:
            self._gtk_comp.set_editable(self._editable)

    def _ensure_selection(self):
        if self._gtk_comp:
            start, end = self._selection
            self._gtk_comp.select_region(start, end)

    def _backend_selection(self):
        if self._gtk_comp:
            start, end = self._gtk_comp.selection_start_pos, \
                        self._gtk_comp.selection_end_pos
            if start > end:
                return end, start
            else:
                return start, end

    def _backend_text(self):
        if self._gtk_comp:
            end = self._gtk_comp.get_length()
            return self._gtk_comp.get_chars(0, end)

################################################################

class Window(ComponentMixin, AbstractWindow):

    _gtk_class = GtkWindow
    _gtk_style = 0
    _visible = 0

    def _ensure_created(self):
        if self._gtk_comp is None:
            self._gtk_comp = self._gtk_class(WINDOW_TOPLEVEL)
            self._gtk_container = GtkLayout()
            self._gtk_comp.add(self._gtk_container)
            self._gtk_container.show()
            self._ensure_geometry()
            self._ensure_title()
            self._ensure_visibility()
            return 1
        return 0

    def _ensure_events(self):
        self._gtk_comp.connect('destroy', self._gtk_close_handler)

    def _ensure_title(self):
        if self._gtk_comp:
            self._gtk_comp.set_title(self._title)

    def _gtk_close_handler(self, *args):
        global _app
        self._gtk_comp.destroy()
        self.destroy()
        _app._window_deleted()

    def _get_gtk_text(self):
        return self._title

    def _gtk_add(self, comp):
        self._gtk_container.put(comp._gtk_comp, comp._x, comp._y)

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

class factory:
    _map = {'Window': Window,
            'Button': Button,
            'CheckBox': CheckBox,
            'RadioButton': RadioButton,
            'RadioGroup': RadioGroup,
            'Application': Application,
            'Label': Label,
            'ListBox': ListBox,
            'TextField': TextField,
            'TextArea': TextArea,
            }
    def get_class(self, name):
        return self._map[name]

# Local Variables:
# compile-command: "pychecker -s gtkgui.py"
# End:
