import weakref as wr
from anygui.backends import *
__all__ = anygui.__all__

######################################################

from qt import *
TRUE = 1
FALSE = 2
DEBUG = 0

class ComponentMixin:

	_qt_comp = None
	_qt_style = None

	def _is_created(self):
		return self._qt_comp is not None

	def _ensure_created(self):
		if DEBUG: print 'in _ensure_created of: ', self
		if not self._qt_comp:
			if self._container:
				parent = self._container._qt_comp
			else:
				parent = None
			if self._qt_class == QWindow:
				new_comp = self._qt_class(parent,self._get_qt_title(),Qt.WDestructiveClose)
			elif hasattr(self,'_get_qt_text') and not self._qt_class is QMultiLineEdit:
				new_comp = self._qt_class(self._get_qt_text(),parent,str(self))
			elif hasattr(self,'_get_qt_title'):
				new_comp = self._qt_class(self._get_qt_title(),parent,str(self))
			else:
				new_comp = self._qt_class(parent,str(self))
			self._qt_comp = new_comp
			return 1
		return 0

	def _ensure_title(self):
		if self._qt_comp:
			if DEBUG: print 'in _ensure_title of: ', self._qt_comp
			self._qt_comp.setCaption(self._get_qt_title())

	def _ensure_text(self):
		if self._qt_comp:
			if DEBUG: print 'in _ensure_text of: ', self._qt_comp
			self._qt_comp.setText(self._get_qt_text())

	def _ensure_geometry(self):
		if self._qt_comp:
			if DEBUG: print 'in _ensure_geometry of: ', self._qt_comp
			self._qt_comp.setGeometry(self._x,self._y,self._width,self._height)

	def _ensure_visibility(self):
		if self._qt_comp:
			if DEBUG:
				print 'in qt _ensure_visibility: ', self._qt_comp
				print 'visible: ', self._visible
			if self._visible:
				if DEBUG: print 'showing component: ', self._qt_comp
				self._qt_comp.show()
			else:
				if DEBUG: print 'hiding component: ', self._qt_comp
				self._qt_comp.hide()

	def _ensure_enabled_state(self):
		if self._qt_comp:
			if DEBUG:
				print 'in qt _ensure_enabled_state: ', self._qt_comp
				print 'enabled: ', self._enabled
			self._qt_comp.setEnabled(self._enabled)

	def _ensure_destroyed(self):
		if self._qt_comp:
			if DEBUG: print 'in qt _ensure_destroyed: ', self._qt_comp
			self._qt_comp.destroy()
			self._qt_comp = None

	def _ensure_events(self):
		pass


#########################################################

class Label(ComponentMixin,AbstractLabel):
	_qt_class = QLabel
	_text = "QLabel"
	_qt_style = Qt.AlignLeft | Qt.AlignVCenter

	def _ensure_created(self):
		result = ComponentMixin._ensure_created(self)
		if result:
			self._qt_comp.setAlignment(self._qt_style)
		return result

	def _ensure_text(self):
		if self._qt_comp:
			self._qt_comp.setText(self._get_qt_text())

	def _get_qt_text(self):
		return self._text

##########################################################

class ListBox(ComponentMixin, AbstractListBox):
	_qt_class = QListBox

	def _backend_selection(self):
		if self._qt_comp:
			return self._qt_comp.currentItem()

	def _ensure_items(self):
		if self._qt_comp:
			self._qt_comp.clear()
			for item in self._items:
				self._qt_comp.insertItem(item,-1)

	def _ensure_events(self):
		if DEBUG: print 'in _ensure_events of: ', self
		qApp.connect(self._qt_comp,SIGNAL('selected (QListBoxItem *)'),self._qt_item_select_handler)

	def _qt_item_select_handler( self, item ):
		if DEBUG: print 'in _qt_lbx_selected of: ', self._qt_comp
		send(self,'select',index=self._qt_comp.index(item),text=str(item.text()))

	def _ensure_selection(self):
		if self._qt_comp:
			self._qt_comp.setCurrentItem(self._selection)


################################################################

class Button(ComponentMixin, AbstractButton):
	_qt_class = QPushButton
	_text = "QPushButton"
	
	def _ensure_events(self):
		if self._qt_comp:
			if DEBUG: print 'in _ensure_events of: ', self._qt_comp
			qApp.connect(self._qt_comp,SIGNAL('clicked()'),self._qt_click_handler)

	def _qt_click_handler(self):
		if DEBUG: print 'in _qt_btn_clicked of: ', self._qt_comp
		send(self,'click')

	def _get_qt_text(self):
		return self._text

class ToggleButtonMixin(ComponentMixin):
	
	def _ensure_state(self):
		if self._qt_comp:
			self._qt_comp.setChecked(self.on)
	
	def _ensure_events(self):
		if DEBUG: print 'in _ensure_events of: ', self._qt_comp
		qApp.connect(self._qt_comp,SIGNAL('clicked()'),self._qt_click_handler)

	def _get_qt_text(self):
		return self._text

class CheckBox(ToggleButtonMixin, AbstractCheckBox):
	_qt_class = QCheckBox
	_text = "QCheckBox"

	def _qt_click_handler(self):
		self.on = self._qt_comp.isChecked()
		send(self, 'click')

class RadioButton(ToggleButtonMixin, AbstractRadioButton):
	_qt_class = QRadioButton
	_text = "QRadioButton"

	def _qt_click_handler(self):
		if self.group is not None:
			for r_btn in self._group._items:
				if r_btn is not self:
					if DEBUG: print '|--> setting %s, with text "%s" to unchecked...' %(r_btn,r_btn._get_qt_text())
					r_btn._qt_comp.setChecked(FALSE)
			self.group.value = self.value
		send(self, 'click')

################################################################

class TextMixin(ComponentMixin, AbstractTextField):
	
	def _backend_text(self):
		if self._qt_comp:
			return str(self._qt_comp.text())

	def _do_ensure_selection(self,ev=None):
		self._ensure_selection()

	def _ensure_editable(self):
		if DEBUG: print 'in _ensure_editable of: ', self._qt_comp
		if self._qt_comp:
			self._qt_comp.setReadOnly(not self._editable)

	def _update_model(self,ev):
		self.model.value = str(self._qt_comp.text())

	def _get_qt_text(self):
		return self._text

class TextField(TextMixin):
	_qt_class = QLineEdit
	_qt_text = 'QLineEdit'

	def _ensure_events(self):
		if self._qt_comp:
			qApp.connect(self._qt_comp,SIGNAL('textChanged(const QString &)'),self._qt_key_press_handler)

	def _ensure_selection(self):
		if self._qt_comp:
			start, end = self._selection
			self._qt_comp.setSelection(start, end-start)

	def _backend_selection(self):
		if self._qt_comp:
			if self._qt_comp.hasMarkedText():
				text = self._backend_text()
				mtxt = str(self._qt_comp.markedText())
				start = text.find(mtxt)
				end = start + len(mtxt)
				return start,  end
			else:
				return None

	def _qt_key_press_handler(self, newText):
		if DEBUG: print 'in _qt_key_pressed of: ', self._qt_comp
		self._text = self._backend_text()
		send(self, 'enterkey')

class TextArea(TextMixin):
	_qt_class = QMultiLineEdit
	_qt_text = 'QMultiLineEdit'

	def _ensure_events(self):
		if self._qt_comp:
			qApp.connect(self._qt_comp,SIGNAL('textChanged()'),self._qt_key_press_handler)

	def _qt_get_lines(self):
		lines = []
		for n in range(1,self._qt_comp.numLines()+1):
			lines.append(self._qt_comp.textLine(n))
		return lines

	def _qt_get_row_col(self, lines, idx):
		row, col, curr_row = 1, 1, 1
		tot_len = 0
		for ln in lines:
			if idx <= len(str(ln)) + tot_len:
				row = curr_row
				col = idx - tot_len
				return row, col
			else:
				curr_row += 1
				tot_len += len(str(ln))
		return row, col

	def _ensure_selection(self):
		#QMultiLineEdit.setSelection is yet to be implemented...
		#Hacked it so that it will work until the proper method can be used.
		if self._qt_comp:
			start, end = self._selection
			lines = self._qt_get_lines()
			srow, scol = self._qt_get_row_col(lines,start)
			erow, ecol = self._qt_get_row_col(lines,end)
			#Enter hack...
			self._qt_comp.setCursorPosition(srow, scol, FALSE)
			self._qt_comp.setCursorPosition(erow, ecol, TRUE)
			#Exit hack...
			#self._qt_comp.setSelection(srow, scol, erow, ecol)

	def _backend_selection(self):
		if self._qt_comp:
			if self._qt_comp.hasMarkedText():
				if DEBUG: print 'in _backend_selection of: ', self._qt_comp
				text = self._backend_text()
				mtxt = str(self._qt_comp.markedText())
				start = text.find(mtxt)
				end = start + len(mtxt)
				if DEBUG: print 'returning start: %s & end: %s' %(start,end)
				return start,  end
			else:
				return None

	def _qt_key_press_handler(self):
		if DEBUG: print 'in _qt_key_pressed of: ', self._qt_comp
		send(self, 'enterkey')

################################################################

class Frame(ComponentMixin, AbstractFrame):
	_qt_class = QFrame
	_qt_style = QFrame.Plain

################################################################

class EventFilterMixin(QObject):
	_window_obj = None
	
	def __init__(self, parent):
		QObject.__init__(self, parent._qt_comp)
		self._window_obj = wr.ref(parent)

	def eventFilter(self, object, event):
		if not event.type() in [QEvent.Resize]:
			return 0
		elif event.type() == QEvent.Resize:
			self._window_obj()._qt_resize_handler(event)
			return 1

class QWindow(QWidget): pass

class Window(ComponentMixin, AbstractWindow):
	_qt_class = QWindow
	_qt_style = None #Check on this...
	_qt_frame = None
	_layout = None
	_title = 'QWindow'

	def _get_panel(self):
		return self._qt_frame

	def _ensure_created(self):
		result = ComponentMixin._ensure_created(self)
		if DEBUG: print 'in _ensure_created of: ', self._qt_comp
		if result:
			self._qt_frame = Frame(self._qt_comp)
			self._ensure_title()
		return result

	def _ensure_events(self):
		if DEBUG: print 'in _ensure_events of: ', self._qt_comp
		self._event_filter = EventFilterMixin(self)
		self._qt_comp.installEventFilter(self._event_filter)
		self._qt_comp.setMouseTracking(TRUE)

	def _get_qt_title(self):
		return self._title

	def _qt_resize_handler(self,event):
		if DEBUG: print 'in _qt_resize_handler of: ', self._qt_comp
		w = self._qt_comp.width()
		h = self._qt_comp.height()
		dw = w - self._width
		dh = h - self._height
		self._width = w
		self._height = h
		self.resized(dw, dh)

################################################################

class Application(AbstractApplication, QApplication):
	def __init__(self, *argv):
		if not argv: argv = list(argv)
		AbstractApplication.__init__(self)
		if not argv: QApplication.__init__(self,argv)
		else: apply(QApplication.__init__,(self,)+argv)
		self.connect(qApp, SIGNAL('lastWindowClosed()'), qApp, SLOT('quit()'))

	def _mainloop(self):
		self.exec_loop()

################################################################
