"Defaults for the anygui package."

# For the Frame.place method:

direction = 'right'
space = 10

class Button:

    _text = 'Button'
    _x = 0
    _y = 0
    _width = 80
    _height = 30
    _hmove = 0
    _vmove = 0
    _hstretch = 0
    _vstretch = 0
    _visible = 1
    _enabled = 1

class CheckBox:

    _text = 'CheckBox'
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

class Frame:

    _text = 'Frame'
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

class ListBox:

    _text = 'ListBox'
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

class RadioButton:
    
    _text = 'RadioButton'
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

class TextArea:

    _text = 'TextArea'
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

class TextField:

    _text = 'TextField'
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

class Window:

    _text = 'Window'
    _x = 30
    _y = 30
    _width = 400
    _height = 300
    _hmove = 0
    _vmove = 0
    _hstretch = 0
    _vstretch = 0
    _visible = 1
    _enabled = 1
    _title = 'Untitled'

def shift_window():
        Window._x += 30
        Window._x %= 360
        Window._y += 30
        Window._y %= 360
