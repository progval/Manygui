"""Defaults for the anygui package.

Each class in module Defaults provides default attributes for the
widget of the same name, plus an attribute named explicit_attributes
that lists the attributes which need to be set explicitly per instance
(currently, the latter defaults to "all defaulted attributes").
"""

# FIXME: Change the default mechanism (i.e. state = {...})

# For the Frame.place method:

direction = 'right'
space = 10

#def _list_attributes(klass):
#    klass.explicit_attributes = klass.__dict__.keys()

class Button:
    state = {
        'text': 'Button',
        'default_event': 'click',
        'x': 0,
        'y': 0,
        'width': 80,
        'height': 30,
        'hmove': 0,
        'vmove': 0,
        'hstretch': 0,
        'vstretch': 0,
        'visible': 1,
        'enabled': 1
        }

class Frame:
    state = {
        'text': 'Frame', # Hardly needed...
        'x': 0,
        'y': 0,
        'width': 400,
        'height': 300,
        'hmove': 0,
        'vmove': 0,
        'hstretch': 0,
        'vstretch': 0,
        'visible': 1,
        'enabled': 1
    }

class Window:
    state = {
        'text': 'Window',
        'x': 30,
        'y': 30,
        'width': 400,
        'height': 300,
        'hmove': 0,
        'vmove': 0,
        'hstretch': 0,
        'vstretch': 0,
        'visible': 1,
        'enabled': 1,
        'title': 'Untitled'
        }

# FIXME: Should be improved -- base new placement on top window etc.

winX, winY = 0, 0
def shift_window():
    global winX, winY
    winX += 30
    winX %= 360
    winY += 30
    winY %= 360

"""
class Canvas:
    _text = 'Canvas' # Hardly needed...
    _x = 0
    _y = 0
    _width = 400
    _height = 300
    _hmove = 0
    _vmove = 0
    _hstretch = 0
    _vstretch = 0
    _visible = 1
    _enabled = 1
_list_attributes(Canvas)

class CheckBox:
    _text = 'CheckBox'
    _default_event = 'click'
    _x = 0
    _y = 0
    _width = 100
    _height = 15
    _hmove = 0
    _vmove = 0
    _hstretch = 0
    _vstretch = 0
    _visible = 1
    _enabled = 1
_list_attributes(CheckBox)

class Label:
    _text = 'Label'
    _x = 0
    _y = 0
    _width = 100
    _height = 15
    _hmove = 0
    _vmove = 0
    _hstretch = 0
    _vstretch = 0
    _visible = 1
    _enabled = 1
_list_attributes(Label)

class ListBox:
    _text = 'ListBox'
    _default_event = 'select'
    _x = 0
    _y = 0
    _width = 100
    _height = 100
    _hmove = 0
    _vmove = 0
    _hstretch = 0
    _vstretch = 0
    _visible = 1
    _enabled = 1
    _items = ()
    _selection = 0
_list_attributes(ListBox)

class RadioButton:
    _text = 'RadioButton'
    _default_event = 'click'
    _x = 0
    _y = 0
    _width = 100
    _height = 15
    _hmove = 0
    _vmove = 0
    _hstretch = 0
    _vstretch = 0
    _visible = 1
    _enabled = 1
_list_attributes(RadioButton)

class RadioGroup:
    _items = None
    _value = None
    _default_event = 'select'
_list_attributes(RadioGroup)

class TextArea:
    _text = ''
    _x = 0
    _y = 0
    _width = 100
    _height = 100
    _hmove = 0
    _vmove = 0
    _hstretch = 0
    _vstretch = 0
    _visible = 1
    _enabled = 1
    _editable = 1
    _selection = (0, 0)
_list_attributes(TextArea)

class TextField:
    _text = ''
    _default_event = 'enterkey'
    _x = 0
    _y = 0
    _width = 100
    _height = 25
    _hmove = 0
    _vmove = 0
    _hstretch = 0
    _vstretch = 0
    _visible = 1
    _enabled = 1
    _editable = 1
    _selection = (0, 0)
_list_attributes(TextField)
"""
