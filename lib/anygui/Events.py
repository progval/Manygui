
''' Event framework for Anygui. For more information, see Anygui
    IRFC 0010 at http://anygui.sf.net/irfc.

    Magnus Lie Hetland, 2001-11-19
'''

__all__ = '''

    connect
    disconnect
    dispatch
    disconnectSource
    disconnectHandler
    disconnectMethods
    Event
    CallbackAdapter

'''.split()


import time
from References import ref, RefKeyDictionary
registry = RefKeyDictionary()
source_stack = []

class Any: pass
any = Any()

def locators(event, weak=0):
    src = ref(getattr(event, 'source', any), weak)
    type = getattr(event, 'type', any)
    return src, type

def connect(event, handler, weak=0):
    'Connect an event pattern to an event handler.'
    src, type = locators(event, weak)
    h = ref(handler, weak)
    if not registry.has_key(src): registry[src] = {}
    try: registry[src][type].append(h)
    except KeyError: registry[src][type] = [h]

def disconnect(event, handler):
    'Disconnect an event handler from an event pattern.'
    h = ref(handler, weak=0)
    for lst in lookup(event):
        try:
            lst.remove(h)
        except (KeyError, ValueError): pass

def set_time(event):
    if not hasattr(event, 'time'):
        try:
            event.time = time.time()
        except TypeError: pass

def lookup(event):
    source, type = locators(event)
    lists = []
    sources = [source]
    if source() is not any: sources.append(ref(any, weak=0))
    types = [type]
    if type is not any: types.append(any)
    for s in sources:
        for t in types:
            try:
                lists.append(registry[s][t])
            except KeyError: pass
    return lists

def dispatch(event):
    'Call the appropriate event handlers with event as the argument. \
    As a side-effect, dead handlers are removed from the candidate lists.'
    source_stack.append(id(getattr(event, 'source', None)))
    try:
        results = []
        set_time(event)
        event.freeze()
        for handlers in lookup(event):
            live_handlers = []
            for r in handlers:
                obj = r.obj
                if obj is not None: obj = obj()
                if obj is not None and id(obj) in source_stack: continue
                if not r.is_dead():
                    live_handlers.append(r)
                    handler = r()
                    result = handler(event)
                    if result is not None: results.append(result)
            handlers[:] = live_handlers
        if results: return results
    finally:
        source_stack.pop()

def disconnectSource(source):
    'Disconnect all handlers connected to a given source.'
    del registry[source]

def disconnectHandler(handler):
    'Disconnect a handler from the event framework.'
    h = ref(handler, weak=0)
    for s in registry.keys():
        for t in registry[s].keys():
            try: retistry[s][t].remove(h)
            except ValueError: pass

def disconnectMethods(obj):
    'Disconnect all the methods of obj that are handlers.'
    for name in dir(obj):
        attr = getattr(obj, name)
        if callable(attr):
            try:
                disconnectHandler(attr)
            except: pass

class Event:
    __frozen = 0
    def __init__(self, **kwds):
        self.__dict__.update(kwds)
    def __setattr__(self, name, value):
        if not self.__frozen:
            self.__dict__[name] = value
        else:
            raise TypeError, 'object has been frozen'
    def freeze(self):
        if not self.__frozen:
            self.__frozen = 1

class CallbackAdapter:
    def dispatch(self, event):
        '''
        If self has a proper callback, call it, then call global
        dispatch().
        '''
        if not hasattr(event, 'source'):
            event.source = self
        set_time(event)
        event.freeze()
        callback = getattr(self, event.type, None)
        if callback:
            result = callback(event)
        results = dispatch(event)
        if results: return [result] + results
        else: return result
