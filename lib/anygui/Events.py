
''' Event framework for Anygui. For more information, see Anygui
    IRFC 0010 at http://anygui.sf.net/irfc.

    Magnus Lie Hetland 2001-11-26
'''

TODO = '''
    - Add tags
    - Fix optional arguments/use of kwdargs in place of positionals etc.
'''

# NOTE: Current semantics (with default events vs. globbing etc.) is
# not necessarily consistent. I'm working on it...     [mlh20011126]

__all__ = '''

    any
    link
    unlink
    send
    unlinkSource
    unlinkHandler
    unlinkMethods

'''.split()


import time
from References import ref, mapping
registry = mapping()
source_stack = []

class Internal: pass
any  = Internal()
void = Internal()

#def link(source, event, handler, tag=void, weak=0, loop=0):
def link(*args, **kwds):
    'Link a source and event to an event handler.'
    assert len(args) < 4, 'link takes only three positional arguments'
    if len(args) == 2:
        source, handler = args; event = 'default'
    else:
        source, event, handler = args
    weak = kwds.get('weak', 0)
    tag  = kwds.get('tag', void)
    #loop = kwds.get('loop', 0)
    s = ref(source, weak)
    h = ref(handler, weak)
    #if tag is not void: h.tag = tag
    if not registry.has_key(s):
        registry[s] = {}
    if not registry[s].has_key(event):
        registry[s][event] = []
    if not h in registry[s][event]:
        registry[s][event].append(h)

#def unlink(source, event, handler, tag=void):
def unlink(*args, **kwds):
    'Unlink an event handler from a source and event.'
    assert len(args) < 4, 'link takes only three positional arguments'
    if len(args) == 2:
        source, handler = args; event = 'default'
    else:
        source, event, handler = args
    tag = kwds.get('tag', void)
    h = ref(handler, weak=0)
    for lst in lookup(source, event, tag):
        try:
            lst.remove(h)
        except (KeyError, ValueError): pass

def lookup(source, event, tag=void):
    source = ref(source, weak=0)
    lists = []
    sources = [source]
    if source() is not any: sources.append(ref(any, weak=0))
    events = [event]
    if event is not any: events.append(any)
    for s in sources:
        for e in events:
            try:
                h = registry[s][e]
                if tag == void or tag == getattr(h,'tag',void):
                    lists.append(registry[s][e])
            except KeyError: pass
    return lists

def send(source, event='default', tag=void, loop=0, **kw):
    'Call the appropriate event handlers with the supplied arguments. \
    As a side-effect, dead handlers are removed from the candidate lists.'
    args = {'source': source, 'event': event}
    args.update(kw)
    if tag is not void: args['tag'] = tag
    source_stack.append(id(source))
    try:
        results = []
        args.setdefault('time', time.time())
        for handlers in lookup(source, event, tag):
            live_handlers = []
            if loop: print handlers
            for r in handlers:
                obj = r.obj
                if obj is not None:
                    obj = obj()
                    if not loop and id(obj) in source_stack: continue
                if not r.is_dead():
                    live_handlers.append(r)
                    handler = r()
                    result = handler(**args)
                    if result is not None: results.append(result)
            handlers[:] = live_handlers
        if results: return results
    finally:
        source_stack.pop()

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
