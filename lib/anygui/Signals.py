"""
Wire signals to slots.

This module contains all the machinery necessary to wire "signals"
(basically, "events") to "slots" (basically, handler code).

Any code that's interested in being informed when a particular signal
is generated by a particular source object can call

Signals.connect(<source>,<signame>,<handler>,<argmap>)

to arrange this. <source> is the object generating the signal;
<signame> is the signal name we're interested in catching; <handler>
is a callable that will be invoked when the signal occurs.

When connect() is called for a particular source, we check whether
the source object has a "connect_request()" method, and if so we
call it with the arguments <signame> and <filter-keywords>. This
allows the source object to perform any backend-specific tasks
necessary in order to generate the requested signal (for example,
registering platform-specific event handler code).

The handler code is invoked with arguments signal_source=<source>,
signal_name=<signame>,and any keyword arguments specified by the signal
sender.

The <source> object may be None, in which case <handler> is
invoked whenever the  given signal is sent, regardless of
source.

Signals.disconnect(<source>,<signame>,<handler>) can be
called to remove any existing association between (<source>,
<signame>) and <handler>. (There is no invocation of a
"signal_disconnect_request()" on the <source>, since that
causes more problems than it's worth.)

Signals.signal(<source>,<signame>,*args,**kws) may be called
anywhere to send the named signal to all registered handlers.
<source> may be None, in which case only default handlers
(those with source==None) will be invoked for the signal.
The *args and *kws are passed intact to the handler function.
Also, keyword arguments "source" and "message" are
added, and indicate the source object and signal name.

The <argmap> provides a means of adapting signals
to arbitrary handlers (in cases where you might need to
call some existing method in response to a signal). The
<argmap> is a dictionary that provides a mapping from
signal keyword data to argument names. Thus if you have code
that sends a signal:

class Attacker:
   def attack(self,target,weapon):
      signal(self,"attack",target=target,weapon=weapon)

and a handler that doesn't care about the "weapon"
argument or the signal name:

def handle_attack(attacker,defender):
    ...

You can connect them by using an argmap to map
the "signal_source" and "target" signal data to the "attacker"
and "defender" handler arguments, respectively:

a = Attacker()
connect(a,"attack",self.handle_attack,
        {"signal_source":"attacker",
         "target":"defender"})

When an argument map is specified, -only- the indicated
arguments are passed to the handler method.

"""

from weakref import *

class _weak_callable:

    def __init__(self,obj,func):
        self._obj = obj
        self._meth = func

    def __call__(self,*args,**kws):
        if self._obj is not None:
            return self._meth(self._obj(),*args,**kws)
        else:
            return self._meth(*args,**kws)

class _handler_adapter(_weak_callable):
    """
    _handler_adapter lets us call any function or method as a
    signal handler, even if it doesn't accept the same
    keyword arguments the signal source provides. ALL
    arguments to a _handler_adapter must be keywords.
    A _handler_adapter is a _weak_callable, which means
    calling it can fail if the associated object has
    been GC'd.
    """

    def __init__(self,obj,meth,argmap=None):
        self._argmap = argmap
        _weak_callable.__init__(self,obj,meth)

    def __call__(self,**kw):
        real_kwargs = {}
        if self._argmap is None:
            real_kwargs.update(kw)

            if str(type(object)) == "<type 'instance'>":
                # instances are callable when they have __call__()
                object = object.__call__

            if hasattr(object, "func_code"):
                # function
                fc = object.func_code
                expected = fc.co_varnames[0:fc.co_argcount]
            elif hasattr(object, "im_func"):
                # method
                fc = object.im_func.func_code
                expected = fc.co_varnames[1:fc.co_argcount]

            # remove unexpected args - co_flags & 0x08 indicates
            # **kws in use, so no need to remove args.
            if not (fc.co_flags & 0x08):
                for name in args.keys():
                    if name not in expected:
                        del args[name]

            return apply(object, (), args)

        else:
            for arg in self._argmap.keys():
                try:
                    real_kwargs[self._argmap[arg]] = kw[arg]
                except KeyError:
                    # OK to send a signal with fewer args.
                    pass
        return _weak_callable.__call__(self,**real_kwargs)

class _weak_ref_fn:
    """ Wraps a function or, more importantly, a bound method, in
    a way that allows a bound method's object to be GC'd, while
    providing the same interface as a normal weak reference. """

    def __init__(self,fn,argmap = None):
        self.argmap = argmap
        try:
            self.obj = ref(fn.im_self)
            self.meth = fn.im_func
        except AttributeError:
            # It's not a bound method.
            self.obj = None
            self.meth = fn

    def __str__(self):
        return "_weak_ref_fn %s: %s %s"%(id(self),self.obj,self.meth)

    def __eq__(self,other):
        if self.obj == other.obj:
            if self.meth == other.meth:
                return 1
        return 0

    def __call__(self):
        if self._dead(): return None
        return _handler_adapter(self.obj,self.meth,self.argmap)

    def _dead(self):
        return self.obj is not None and self.obj() is None

    def __getattr__(self,attr):
        if attr == 'im_self':
            if self.obj is None:
                return None
            return self.obj()
        if attr == 'im_func':
            return self.meth
        raise AttributeError, attr

class _href:
    """ A weakref that is always hashable. We need this
    to maintain signal maps for source objects that might
    not be naturally hashable. The hash value is just
    the object address. This might break on some platforms,
    please email jknapka@earthlink.net if so. """

    def __init__(self,obj):
        if obj is None:
            self.ref = None
        else:
            self.ref = ref(obj)

    def __call__(self):
        if self.ref is None:
            return None
        return self.ref()

    def __cmp__(self,other):
        if id(self.ref)<id(other.ref): return 1
        if id(self.ref)>id(other.ref): return -1
        return 0

    def __hash__(self):
        return id(self.ref)

class SignalException:
    """ Exception raised when a signal can't be delivered. """
    def __init__(self,**kw):
        self.__dict__.update(kw)

class _signal_map:
    """
    _signal_map represents the signal-to-handler mapping for a
    single source object.
    """

    def __init__(self,source):
        self._source = source
        self._sigmap = {}

    def connect(self,signame,handler,argmap=None):
        """ Add a handler for <signame> """
        rh = _weak_ref_fn(handler,argmap)
        try:
            if rh in self._sigmap[signame]:
                return
            self._sigmap[signame].append(rh)
        except KeyError:
            # Signame not mapped yet.
            self._sigmap[signame] = [rh]
        if self._source is not None:
            try:
                self._source().connect_request(signame)
            except AttributeError:
                pass # Ok not to implement connect_request()

    def disconnect(self,signame,handler):
        """ Remove a handler for <signame> """
        rh = _weak_ref_fn(handler)
        try:
            self._sigmap[signame].remove(rh)
        except (KeyError,ValueError):
            # Signame not mapped; OK.
            pass

    def disconnect_handler_object(self,handler_obj):
        """ Remove all handlers associated with handler_obj """
        for sig in self._sigmap.keys():
            rmv = []
            for hdlr in self._sigmap[sig]:
                if hdlr.im_self is handler_obj:
                    rmv.append(hdlr)
            for hdlr in rmv:
                self._sigmap[sig].remove(hdlr)

    def remove_dead_handlers(self,sig=None):
        """ Remove GC'd signal handlers for the <sig> signal
        If <sig> is None, we do this for every signal. """
        if sig is None:
            # Remove all dead handlers.
            for sig in self._sigmap.keys():
                self.remove_dead_handlers(sig)
            return

        # Remove dead handlers only for sig.
        live_handlers = []
        try:
            for hdlr in self._sigmap[sig]:
                if hdlr() is not None:
                    live_handlers.append(hdlr)
        except KeyError:
            # The signal had no map.
            pass
        self._sigmap[sig] = live_handlers

    def send_signal(self,signame,signal_source=None,**kws):
        """ Send the given signal and associated data to all handlers. """

        # Don't try to invoke dead handlers.
        self.remove_dead_handlers(signame)

        src = signal_source
        if src is None and self._source is not None:
            src = self._source()
            if src is None:
                # Source object has been gc'd, so we shouldn't
                # be sending any signals from it!
                raise SignalException,"Source object no longer exists"

        # Deliver the signal and associated data to all handlers.
        try:
            for hdlr in self._sigmap[signame]:
                hdlr()(source=src,message=signame,**kws)
        except KeyError:
            # No handlers for the signal
            pass
        try:
            for hdlr in self._sigmap[None]:
                hdlr()(signal_source=src,signal_name=signame,**kws)
        except KeyError:
            # No handlers for the signal
            pass

# The map of signal sources to handlers. Keys
# are weakref-to-source, unless source is None, in which case
# the source is just None. The values are _signal_map objects.
_global_sig_map = {None:_signal_map(None)}
_sig_map_cleanup_count = 0
sig_map_cleanup_interval = 100

def remove_dead_sources():
    """ Remove handlers associated with GC'd sources.

    You should not normally have to call this function.
    """
    for src in _global_sig_map.keys():
        if src is not None:
            if src() is None:
                del _global_sig_map[src]

def get_source_ref(source):
    rs = None
    if source != None:
        rs = _href(source)
    return rs

def connect(source,signame,handler,argmap=None):
    """
    Construct a mapping from <source>'s signal <signame> to
    the given <handler>. If "argmap" is specified, it must be
    a dictionary mapping signal keyword arguments to handler
    keyword arguments. In such cases, ONLY the keywords specified
    in the argmap will be passed to the handler. If no argmap
    is specified, ALL signal keyword are passed as keyword
    arguments to the handler. The special keywords
    "signal_source" and "signal_name", containing the source
    object reference (if any) and the signal name, are added
    to all signal events (though they are only passed to
    the handler if the argmap is None or specifies a mapping
    for them).
    """
    rs = get_source_ref(source)
    map = None
    try:
        map = _global_sig_map[rs]
    except KeyError:
        map = _signal_map(rs)
        _global_sig_map[rs] = map
    map.connect(signame,handler,argmap)

def disconnect(source,signame,handler):
    """
    Remove all associations between <source>'s <signame> and
    the given <handler>.
    """
    rs = get_source_ref(source)
    map = None
    try:
        map = _global_sig_map[rs]
    except KeyError:
        # Signal not mapped; OK.
        return
    map.disconnect(signame,handler)

def disconnect_handler_object(handler,source=None):
    """
    Disconnect -all- signals handled by <handler>'s methods.
    If <source> is supplied, only disconnect signals generated
    by <source>
    """
    source = get_source_ref(source)
    if source is None:
        for src in _global_sig_map.keys():
            disconnect_handler_object(handler,src)
        return

    try:
        _global_sig_map[source].disconnect_handler_object(handler)
    except KeyError:
        pass # Maybe this source has no receivers.

"""
signal_stack is an ordered list of all objects that are
currently sending signals, and the signal name of each
signal call, as tuples. Each send_signal caller and
signal name are appended to the list, and then removed
when their signal has been processed.
"""
signal_stack = []

def signal(source,signame,**kws):
    """
    Send <signame> from <source> to all handlers, passing the
    <source>, <signame>, *args, and *kws intact.
    """

    global signal_stack
    signal_stack.append((source,signame))

    try:
        global _sig_map_cleanup_count
        _sig_map_cleanup_count += 1
        if _sig_map_cleanup_count >= sig_map_cleanup_interval:
            remove_dead_sources()
            _sig_map_cleanup_count = 0
        
        rs = get_source_ref(source)
        try:
            map = _global_sig_map[rs]
            map.send_signal(signame,**kws)
        except KeyError:
            # Signal not mapped; OK.
            pass
    
        # Now send to default handlers (unless we already did so).
        if rs is not None:
            map = _global_sig_map[None]
            map.send_signal(signame,signal_source=rs(),**kws)
    finally:
        # Pop the signal stack.
        signal_stack = signal_stack[:-1]

class _call_adapter:

    def __init__(self,src,callable,attr):
        self.src = src
        self.meth = callable
        self.attr = attr

    def __getattr__(self,attr):
        return getattr(self.meth,attr)

    def __call__(self,*args,**kws):
        result = self.meth(*args,**kws)
        signal(self.src,self.attr,args=args,**kws)
        return result

class SignalAdapter:
    """ SignalAdapter allows any object to be adapted to send
    signals when selected method calls or attribute modifications
    occur. For example, if you have

    class Model:
        def set_state(self,state):
            self.state = state
    m = Model()
    
    and you would like a signal to be generated after every
    set_state call on m and whenever m's "affinity" attribute
    is modified, then instead of using Model directly, do this:

    m = SignalAdapter(Model(),["set_state","affinity"])

    Then, whenever m.set_state(<state>) is called, signal
    "set_state" with source m will be sent, with a
    keyword argument args=(<state>);
    and whenever m.affinity = <value> is called,
    a signal "affinity" will be sent with source "m"
    and keyword argument new_value=<value>.
    """

    def __init__(self,obj,siglist):
        self.__obj = obj
        self.__siglist = siglist

    def __getattr__(self,attr):
        print "getattr %s"%attr
        if attr in ['_SignalAdapter__obj','_SignalAdapter__siglist']:
            return self.__dict__[attr]
        if attr in self.__siglist:
            meth = getattr(self.__obj,attr)
            ca = _call_adapter(self,meth,attr)
            return ca
        else:
            return getattr(self.__obj,attr)

    def __setattr__(self,attr,value):
        print "setattr %s %s"%(attr,value)
        if attr in ['_SignalAdapter__obj','_SignalAdapter__siglist']:
            self.__dict__[attr] = value
            return
        setattr(self.__obj,attr,value)
        if attr in self.__siglist:
            signal(self,attr,new_value=value)
