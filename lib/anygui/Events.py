
''' Event framework for Anygui. For more information, see Anygui
    IRFC 0010 at http://anygui.sf.net/irfc.
'''

# TODO: - Use some internal value instead of None for defaults
#       - Add tags
#       - Fix optional arguments
#       - loop arg should perhaps be in link? Or both?

__all__ = '''

    link
    unlink
    send
    unlinkSource
    unlinkHandler
    unlinkMethods

'''.split()


import time
from References import ref, RefKeyDictionary
registry = RefKeyDictionary()
source_stack = []

class Any: pass
any = Any()

def link(source, event, handler, weak=0):
    'Link a source and event to an event handler.'
    s = ref(source, weak)
    h = ref(handler, weak)
    if not registry.has_key(s):
        registry[s] = {}
    if not registry[s].has_key(event):
        registry[s][event] = []
    if not h in registry[s][event]:
        registry[s][event].append(h)

def unlink(source, event, handler):
    'Unlink an event handler from an event pattern.'
    h = ref(handler, weak=0)
    for lst in lookup(source, event):
        try:
            lst.remove(h)
        except (KeyError, ValueError): pass

def set_time(args):
    if not args.has_key('time'):
        args['time'] = time.time()

def lookup(source, event):
    source = ref(source, weak=0)
    lists = []
    sources = [source]
    if source() is not any: sources.append(ref(any, weak=0))
    events = [event]
    if event is not any: events.append(any)
    for s in sources:
        for e in events:
            try:
                lists.append(registry[s][e])
            except KeyError: pass
    return lists

# TODO: Add defaults etc.
def send(source, event, loop=0, **kw):
    'Call the appropriate event handlers with the supplied arguments. \
    As a side-effect, dead handlers are removed from the candidate lists.'
    args = {'source': source, 'event': event, 'loop': loop}
    args.update(kw)
    if not loop: source_stack.append(id(source))
    try:
        results = []
        set_time(args)
        for handlers in lookup(source, event):
            live_handlers = []
            for r in handlers:
                obj = r.obj
                if obj is not None: obj = obj()
                if obj is not None and id(obj) in source_stack: continue
                if not r.is_dead():
                    live_handlers.append(r)
                    handler = r()
                    result = handler(**args)
                    if result is not None: results.append(result)
            handlers[:] = live_handlers
        if results: return results
    finally:
        if not loop: source_stack.pop()

def unlinkSource(source):
    'Unlink all handlers linked to a given source.'
    del registry[source]

def unlinkHandler(handler):
    'Unlink a handler from the event framework.'
    h = ref(handler, weak=0)
    for s in registry.keys():
        for e in registry[s].keys():
            try: retistry[s][e].remove(h)
            except ValueError: pass

def unlinkMethods(obj):
    'Unlink all the methods of obj that are handlers.'
    for name in dir(obj):
        attr = getattr(obj, name)
        if callable(attr):
            try:
                unlinkHandler(attr)
            except: pass

"""
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
    def send(self, event):
        '''
        If self has a proper callback, call it, then call global
        send().
        '''
        if not hasattr(event, 'source'):
            event.source = self
        set_time(event)
        event.freeze()
        callback = getattr(self, event.type, None)
        if callback:
            result = callback(event)
        results = send(event)
        if results: return [result] + results
        else: return result
"""
