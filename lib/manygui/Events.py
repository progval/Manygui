
TODO = '''
    - Fix optional arguments/use of kwdargs in place of positionals etc.
'''

__all__ = '''

    any
    link
    unlink
    send
    sender
    caller
    unlinkSource
    unlinkHandler
    unlinkMethods

'''.split()


import time
import collections
registry = {}
from .Utils import IdentityStack, Bunch
from .Attribs import Attrib
import manygui.Devices as Devices
handler_stack = IdentityStack()
source_stack = IdentityStack()

class any:
    pass

#========================================================#
# Event classes

class AbstractEvent(Attrib):
    """Base event."""

    state = {
        'device': None,
        'time': None,
        'source': None
        }

    def __init__(self, *args, **kwargs):
        Attrib.__init__(self, *args, **kwargs)
        self.time = time.time()

class SelectEvent(AbstractEvent):
    item = None

class ToggleEvent(AbstractEvent):
    pass

class CloseEvent(AbstractEvent):
    pass

####################
# System events

class SystemEvent(AbstractEvent):
    pass

class ShutdownEvent(SystemEvent):
    pass

####################
# MVC events

class ModelEvent(AbstractEvent):
    pass

class UpdateEvent(ModelEvent):
    pass

####################
# File events

class FileEvent(AbstractEvent):
    pass

class OpenFileEvent(FileEvent):
    pass

####################
# Mouse events

class MouseEvent(AbstractEvent):
    device = Devices.Mouse()
    component = None

class LeftClickEvent(MouseEvent):
    pass

class RightClickEvent(MouseEvent):
    pass

class MouseSelectEvent(MouseEvent, SelectEvent):
    pass

####################
# Keyboard events

class KeyboardEvent(AbstractEvent):
    device = Devices.Keyboard()
    component = None
    text = None

class TextInputEvent(KeyboardEvent):
    device = Devices.Keyboard()
    component = None

class PressEnterEvent(KeyboardEvent):
    pass

#=============================================================#
# Functions

#def link(source, event, handler,  weak=0, loop=0):
def link(*args, **kwds):
    'Link a source and event to an event handler.'
    assert len(args) < 4, 'link takes only three positional arguments'
    if len(args) == 2:
        source, handler = args
        assert hasattr(source, '_defaultEvent'), \
                'Source provides no default event.'
        event = source._defaultEvent
    else:
        source, event, handler = args
    weak = kwds.get('weak', 0)
    loop = kwds.get('loop', 0)
    handler.__dict__['loop'] = loop
    if source not in registry:
        registry[source] = {}
    if event not in registry[source]:
        registry[source][event] = []
    if not handler in registry[source][event]:
        registry[source][event].append(handler)
    prodder = getattr(source, 'enableEvent', None)
    if isinstance(prodder, collections.Callable): prodder(event)

#def unlink(source, event, handler):
def unlink(*args, **kwds):
    'Unlink an event handler from a source and event.'
    assert len(args) < 4, 'link takes only three positional arguments'
    if len(args) == 2:
        source, handler = args
        assert hasattr(source, '_defaultEvent'), \
                'Source provides no default event.'
        event = source._defaultEvent
    else:
        source, event, handler = args
    try:
        registry[source][event].remove(handler)
    except (KeyError, ValueError): pass

def lookup(source, event):
    if event is None:
        event = source._defaultEvent

    # Filter by source
    events = {}
    if source in registry:
        events.update(registry[source])
    if any in registry:
        for event, lst in registry[any].items():
            if event in events:
                events[event].extend(lst)
            else:
                events.update({event: lst})

    # Filter by event
    lst = []
    if event in events:
        lst += events[event]
    if any in events:
        lst += events[any]
    return lst

def send(source, event=None, loop=0):
    'Call the appropriate event handlers with the supplied arguments. \
    As a side-effect, dead handlers are removed from the candidate lists.'
    assert source is not any
    assert event is not any
    if event is None:
        assert hasattr(source, '_defaultEvent'), \
                'Source provides no default event.'
        event = source._defaultEvent()
    event.source, event.time = source, time.time()
    source_stack.append(source)
    try:
        results = []
        for handler in lookup(source, event.__class__):
            if handler is not None:
                if not loop and not handler.loop \
                        and (handler in source_stack or
                                handler in handler_stack):
                    continue
                handler_stack.append(handler)
                try:
                    result = handler(event)
                finally:
                    handler_stack.pop()
            if result is not None: results.append(result)
        if results: return results
    finally:
        source_stack.pop()

class Sender:
    def __init__(self, event):
        self.event = event
    def __call__(self, source, event):
        if self.event is None:
            event = source._defaultEvent
        else:
            event = self.event
        send(source, event())

sender = Sender

class Caller:
    def __init__(self, func, args, kwds):
        self.func = func
        self.args = args
        self.kwds = kwds
    def __call__(self, *args, **kwds):
        return self.func(*self.args, **self.kwds)

caller = Caller

def unlinkSource(source):
    'Unlink all handlers linked to a given source.'
    del registry[source]

def unlinkHandler(handler):
    'Unlink a handler from the event framework.'
    for source in list(registry.keys()):
        for event in list(registry[source].keys()):
            try: registry[source][event].remove(handler)
            except ValueError: pass

def unlinkMethods(obj):
    'Unlink all the methods of obj that are handlers.'
    for name in dir(obj):
        attr = getattr(obj, name)
        if isinstance(attr, collections.Callable):
            try:
                unlinkHandler(attr)
            except: pass
