from anygui.backends import *
__all__ = anygui.__all__

######################################################
from weakref import ref as wr
from qt import *
TRUE = 1
FALSE = 0

DEBUG = 1
TMP_DBG = 1

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
				new_comp = self._qt_class(parent,self._get_qt_title())
			elif hasattr(self,'_get_qt_text') and not self._qt_class is QMultiLineEdit:
				new_comp = self._qt_class(self._get_qt_text(),parent,str(self))
			elif hasattr(self,'_get_qt_title'):
				new_comp = self._qt_class(self._get_qt_title(),parent,str(self))
			else:
				new_comp = self._qt_class(parent,str(self))
			self._qt_comp = new_comp
			return 1
		return 0

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
			try: self._connected = 0
			except: pass
			self._qt_comp.destroy()
			self._qt_comp = None

	def _ensure_events(self):
		pass


#########################################################

class Label(ComponentMixin,AbstractLabel):
	_qt_class = QLabel
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
	_connected = 0
	
	def _ensure_events(self):
		if DEBUG: print 'in _ensure_events of: ', self
		if self._qt_comp and not self._connected:
			qApp.connect(self._qt_comp,SIGNAL('selected (QListBoxItem *)'),self._qt_item_select_handler)
			self._connected = 1

	def _ensure_items(self):
		if self._qt_comp:
			self._qt_comp.clear()
			for item in self._items:
				self._qt_comp.insertItem(item,-1)

	def _ensure_selection(self):
		if self._qt_comp:
			self._qt_comp.setCurrentItem(self._selection)

	def _backend_selection(self):
		if self._qt_comp:
			return self._qt_comp.currentItem()

	def _qt_item_select_handler( self, item ):
		if DEBUG: print 'in _qt_item_select_handler of: ', self._qt_comp
		#send(self,'select',index=self._qt_comp.index(item),text=str(item.text()))
		send(self,'select')


################################################################

class ButtonBase(ComponentMixin):
	_connected = 0

	def _ensure_events(self):
		if self._qt_comp and not self._connected:
			if DEBUG: print 'in _ensure_events of: ', self._qt_comp
			qApp.connect(self._qt_comp,SIGNAL('clicked()'),self._qt_click_handler)
			self._connected = 1

	def _ensure_text(self):
		if self._qt_comp:
			if DEBUG: print 'in _ensure_text of: ', self._qt_comp
			self._qt_comp.setText(QString(self._get_qt_text()))

	def _get_qt_text(self):
		return self._text

class Button(ButtonBase, AbstractButton):
	_qt_class = QPushButton

	def _qt_click_handler(self):
		if DEBUG: print 'in _qt_btn_clicked of: ', self._qt_comp
		send(self,'click')

class ToggleButtonBase(ButtonBase):
	
	def _ensure_state(self):
		if DEBUG: print 'in _ensure_state of: ', self._qt_comp
		if self._qt_comp:
			if not self._qt_comp.isChecked() == self._on:
				self._qt_comp.setChecked(self._on)

class CheckBox(ToggleButtonBase, AbstractCheckBox):
	_qt_class = QCheckBox

	def _qt_click_handler(self):
		val = self._qt_comp.isChecked()
		if self.on == val:
			return
		self.modify(on=val)
		send(self, 'click')

class RadioButton(ToggleButtonBase, AbstractRadioButton):
	_qt_class = QRadioButton

	def _qt_click_handler(self):
		if DEBUG: print 'in _qt_click_handler of: ', self._qt_comp
		val = self._qt_comp.isChecked()
		if self._on == val:
			return
		if self.group is not None:
			self.group.modify(value=self.value)
		send(self, 'click')

################################################################

class TextBase(ComponentMixin, AbstractTextField):
	_connected = 0

	def _ensure_text(self):
		if self._qt_comp:
			if DEBUG: print 'in _ensure_text of: ', self._qt_comp
			self._qt_comp.setText(self._get_qt_text())

	def _ensure_editable(self):
		if DEBUG: print 'in _ensure_editable of: ', self._qt_comp
		if self._qt_comp:
			self._qt_comp.setReadOnly(not self._editable)

	def _backend_text(self):
		if self._qt_comp:
			return str(self._qt_comp.text())

	def _get_qt_text(self):
		return QString(self._text)

	def _calc_start_end(self,text,mtxt,pos):
		start, idx = 0, -1
		for n in range(text.count(mtxt)):
			idx = text.find(mtxt, idx+1)
			if idx == pos or idx == pos - len(mtxt):
				start = idx
				break
		end = start + len(mtxt)
		if DEBUG: print 'returning => start: %s | end: %s' %(start,end)
		return start,  end

class TextField(TextBase):
	_qt_class = QLineEdit

	def _ensure_events(self):
		if self._qt_comp and not self._connected:
			qApp.connect(self._qt_comp,SIGNAL('textChanged(const QString &)'),self._qt_key_press_handler)
			self._connected = 1

	def _ensure_selection(self):
		if self._qt_comp:
			if DEBUG: print 'in _ensure_selection of: ', self._qt_comp
			start, end = self._selection
			self._qt_comp.setSelection(start, end-start)
			self._qt_comp.setCursorPosition(end)

	def _backend_selection(self):
		if self._qt_comp:
			if self._qt_comp.hasMarkedText():
				if DEBUG: print 'in _backend_selection of: ', self._qt_comp
				text = self._backend_text()
				mtxt = str(self._qt_comp.markedText())
				pos = self._qt_comp.cursorPosition()
				return self._calc_start_end(text,mtxt,pos)
			else:
				return 0, 0

	def _qt_key_press_handler(self, newText):
		if DEBUG: print 'in _qt_key_pressed of: ', self._qt_comp
		self.modify(text=self._backend_text())
		send(self, 'enterkey')

class TextArea(TextBase):
	_qt_class = QMultiLineEdit

	def _ensure_events(self):
		if self._qt_comp and not self._connected:
			qApp.connect(self._qt_comp,SIGNAL('textChanged()'),self._qt_key_press_handler)
			self._connected = 1

	def _ensure_selection(self):
		#QMultiLineEdit.setSelection is yet to be implemented...
		#Hacked it so that it will work until the proper method can be used.
		if self._qt_comp:
			start, end = self._selection
			lines = self._qt_get_lines()
			srow, scol = self._qt_translate_row_col(lines,start)
			erow, ecol = self._qt_translate_row_col(lines,end)
			#Enter hack...
			self._qt_comp.setCursorPosition(srow, scol, FALSE)
			self._qt_comp.setCursorPosition(erow, ecol, TRUE)
			#Exit hack...
			#self._qt_comp.setSelection(srow, scol, erow, ecol)
			#self._qt_comp.setCursorPosition(erow,ecol)

	def _backend_selection(self):
		if self._qt_comp:
			if self._qt_comp.hasMarkedText():
				if DEBUG: print 'in _backend_selection of: ', self._qt_comp
				text = self._backend_text()
				mtxt = str(self._qt_comp.markedText())
				row, col = self._qt_comp.getCursorPosition()
				if DEBUG: print 'row, col -> %s, %s' %(row,col) 
				pos = self._qt_translate_position(row, col)
				if DEBUG: print 'pos of cursor is: ', pos
				return self._calc_start_end(text,mtxt,pos)
			else:
				return 0, 0

	def _qt_get_lines(self):
		lines = []
		for n in range(1,self._qt_comp.numLines()):
			lines.append(str(self._qt_comp.textLine(n)) + '\n')
		print 'lines are: \n', lines
		return lines

	def _qt_translate_row_col(self, lines, pos):
		row, col, curr_row = 0, 0, 0
		tot_len = 0
		for ln in lines:
			if pos <= len(str(ln)) + tot_len:
				row = curr_row
				col = pos - tot_len
				return row, col
			else:
				curr_row += 1
				tot_len += len(str(ln))
		return row, col

	def _qt_translate_position(self, row, col):
		if DEBUG: print 'translating row/col to pos...'
		lines = self._qt_get_lines()
		pos = 0
		for n in range(len(lines)):
			if row != n:
				pos += len(lines[n])
			else:
				pos += col
				break
		if DEBUG: print 'returning pos -> ', pos
		return pos

	def _qt_key_press_handler(self):
		if DEBUG: print 'in _qt_key_pressed of: ', self._qt_comp
		self.modify(text=self._backend_text())
		send(self, 'enterkey')


################################################################

class Frame(ComponentMixin, AbstractFrame):
	_qt_class = QFrame
	_qt_style = QFrame.Plain

################################################################

class EventFilter(QObject):
	_window_obj = None
	
	def __init__(self, parent):
		QObject.__init__(self, parent._qt_comp)
		self._window_obj = wr(parent)

	def eventFilter(self, object, event):
		#if DEBUG: print 'in eventFilter of: ', self._window_obj()._qt_comp
		if not event.type() in [QEvent.Resize]: # More??
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
	_connected = 0

	def _ensure_created(self):
		result = ComponentMixin._ensure_created(self)
		if DEBUG: print 'in _ensure_created of: ', self._qt_comp
		if result:
			self._qt_frame = Frame(self._qt_comp)
			self._ensure_title()
		return result

	def _ensure_title(self):
		if self._qt_comp:
			if DEBUG: print 'in _ensure_title of: ', self._qt_comp
			self._qt_comp.setCaption(self._get_qt_title())

	def _ensure_events(self):
		if DEBUG: print 'in _ensure_events of: ', self._qt_comp
		if self._qt_comp and not self._connected:
			self._event_filter = EventFilter(self)
			self._qt_comp.installEventFilter(self._event_filter)
			self._qt_comp.setMouseTracking(TRUE)
			self._connected = 1

	def _get_qt_title(self):
		return self._title

	def _get_panel(self):
		return self._qt_frame

	def _qt_resize_handler(self,event):
		if DEBUG: print 'in _qt_resize_handler of: ', self._qt_comp
		w = self._qt_comp.width()
		h = self._qt_comp.height()
		dw = w - self._width
		dh = h - self._height
		self.modify(width=w)
		self.modify(height=h)
		self.resized(dw, dh)

################################################################

class Application(AbstractApplication, QApplication):

	def __init__(self, *argv):
		AbstractApplication.__init__(self)
		if not argv:
			argv = list(argv)
			QApplication.__init__(self,argv)
		else: 
			apply(QApplication.__init__,(self,)+argv)
		self.connect(qApp, SIGNAL('lastWindowClosed()'), qApp, SLOT('quit()'))

	def _mainloop(self):
		self.exec_loop()

################################################################
