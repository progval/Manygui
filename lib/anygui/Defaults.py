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
    _default_event = 'click'
    state = {
        'text': 'Button',
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

class Label:
    state = {
        'text': 'Label',
        'x': 0,
        'y': 0,
        'width': 100,
        'height': 15,
        'hmove': 0,
        'vmove': 0,
        'hstretch': 0,
        'vstretch': 0,
        'visible': 1,
        'enabled': 1,
        }

class TextField:
    state = {
        'text' : '',
        'default_event' : 'enterkey',
        'x' : 0,
        'y' : 0,
        'width' : 100,
        'height' : 25,
        'hmove' : 0,
        'vmove' : 0,
        'hstretch' : 0,
        'vstretch' : 0,
        'visible' : 1,
        'enabled' : 1,
        'editable' : 1,
        'selection' : (0, 0),
        }

# FIXME: Should be improved -- base new placement on top window etc.

winX, winY = 0, 0
def shift_window():
    global winX, winY
    winX += 30
    winX %= 360
    winY += 30
    winY %= 360

class Canvas:
    state = {
        'text' : 'Canvas', # Hardly needed...,
        'x' : 0,
        'y' : 0,
        'width' : 400,
        'height' : 300,
        'hmove' : 0,
        'vmove' : 0,
        'hstretch' : 0,
        'vstretch' : 0,
        'visible' : 1,
        'enabled' : 1,
        }

class CheckBox:
    state = {
        'text' : 'CheckBox',
        'default_event' : 'click',
        'x' : 0,
        'y' : 0,
        'width' : 100,
        'height' : 15,
        'hmove' : 0,
        'vmove' : 0,
        'hstretch' : 0,
        'vstretch' : 0,
        'visible' : 1,
        'enabled' : 1,
        }

class ListBox:
    state = {
        'text' : 'ListBox',
        'default_event' : 'select',
        'x' : 0,
        'y' : 0,
        'width' : 100,
        'height' : 100,
        'hmove' : 0,
        'vmove' : 0,
        'hstretch' : 0,
        'vstretch' : 0,
        'visible' : 1,
        'enabled' : 1,
        'items' : (),
        'selection' : 0,
        }
    
class RadioButton:
    state = {
        'text' : 'RadioButton',
        'default_event' : 'click',
        'x' : 0,
        'y' : 0,
        'width' : 100,
        'height' : 15,
        'hmove' : 0,
        'vmove' : 0,
        'hstretch' : 0,
        'vstretch' : 0,
        'visible' : 1,
        'enabled' : 1,
        }

class RadioGroup:
    state = {
        'items' : None,
        'value' : None,
        'default_event' : 'select',
        }

class TextArea:
    state = {
        'text' : '',
        'x' : 0,
        'y' : 0,
        'width' : 100,
        'height' : 100,
        'hmove' : 0,
        'vmove' : 0,
        'hstretch' : 0,
        'vstretch' : 0,
        'visible' : 1,
        'enabled' : 1,
        'editable' : 1,
        'selection' : (0, 0),
        }
