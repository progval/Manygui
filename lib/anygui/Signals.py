"""
Wire signals to slots.

This module contains all the machinery necessary to wire "signals"
(basically, "events") to "slots" (basically, handler code).

Any code that's interested in being informed when a particular signal
is generated by a particular sender object can call

Signals.connect(<sender>,<message>,<handler>,<**kws>)

to arrange this. <sender> is the object generating the signal;
<message> is the signal name we're interested in catching; <handler>
is a callable that will be invoked when the signal occurs.
There is a variation to the connect() call that can be used
when it's necessary to adapt signal parameters to handler
parameters via an adapter function; see the connect()
documentation for details.

When connect() is called for a particular sender, we check whether
the sender object has a "connect_request()" method, and if so we
call it with the arguments message=message and **kws . This
allows the sender object to perform any backend-specific tasks
necessary in order to generate the requested signal (for example,
registering platform-specific event handler code).

The handler code is invoked with arguments sender=<sender>,
message=<message>,and any keyword arguments specified by the signal
sender.

The <sender> argument may be None, in which case <handler> is
invoked whenever the  given signal is sent, regardless of
sender.

Signals.disconnect(<sender>,<message>,<handler>) can be
called to remove any existing association between (<sender>,
<message>) and <handler>.

Signals.signal(<sender>,<message>,**kws) may be called
anywhere to send the named signal to all registered handlers.
<sender> may be None, in which case only default handlers
(those with sender==None) will be invoked for the signal.
Only the *kws accepted by the handler are passed to the
handler function. Also, keyword arguments "sender" and
"message" are added (if the handler can accept them), and
indicate the sender object and signal name.

"""

from weakref import *

class SignalException:
    """ Exception raised when a signal can't be delivered. """
    def __init__(self,**kw):
        self.__dict__.update(kw)

class _weak_callable:

    def __init__(self,obj,func):
        try:
            self._obj = ref(obj)
        except TypeError:
            self._obj = None
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
    keyword arguments the signal sender provides. ALL
    arguments to a _handler_adapter must be keywords.
    A _handler_adapter is a _weak_callable, which means
    calling it can fail if the associated object has
    been GC'd.
    """

    def __init__(self,obj,meth):
        _weak_callable.__init__(self,obj,meth)

    def __call__(self,**kw):
        args = kw

        func = self._meth

        if str(type(func)) == "<type 'instance'>":
            # instances are callable when they have __call__()
            func = func.__call__

        if hasattr(func, "func_code"):
            # function
            fc = func.func_code
            expected = fc.co_varnames[0:fc.co_argcount]
        elif hasattr(func, "im_func"):
            # method
            fc = func.im_func.func_code
            expected = fc.co_varnames[1:fc.co_argcount]
            
        # remove unexpected args - co_flags & 0x08 indicates
        # **kws in use, so no need to remove args.
        if not (fc.co_flags & 0x08):
            for name in args.keys():
                if name not in expected:
                    del args[name]

        if self._obj is None:
            the_self = ()
        else:
            the_self = (self._obj(),)

        return apply(func, the_self, args)

class _weak_ref_fn:
    """ Wraps a function or, more importantly, a bound method, in
    a way that allows a bound method's object to be GC'd, while
    providing the same interface as a normal weak reference. """

    def __init__(self,fn,handler=None):
        if handler is not None:
            # fn is an unbound method or adapter, handler
            # is the object on which it should be invoked.

            # First, check to be -sure- fn is not a bound
            # method, or if it is, that handler == fn.im_self:
            try:
                obj = fn.im_self
                if obj is not handler:
                    raise SignalException(msg="Handler obj doesn't match bound handler!")
                self.obj = ref(obj)
                self.meth = fn.im_func
            except AttributeError:
                # Not a bound method, cool.
                pass
            try:
                self.obj = ref(handler)
            except TypeError:
                self.obj = None
            self.meth = fn
            return
        try:
            # Is fn a bound method? If so, convert it into
            # a weakref-to-obj+unbound-method.
            self.obj = ref(fn.im_self)
            self.meth = fn.im_func
        except AttributeError:
            # It's a global function or other callable.
            self.obj = None
            self.meth = fn

    def __str__(self):
        return "_weak_ref_fn %s: %s %s"%(id(self),self.obj,self.meth)

    def __eq__(self,other):
        #print "is %s == %s?"%(self,other)
        if self.obj == other.obj:
            #print "self.obj match"
            if self.meth == other.meth:
                #print "YES"
                return 1
        #print "NO"
        return 0

    def __call__(self):
        if self._dead(): return None
        obj = self.obj
        if obj is not None: obj = obj()
        return _handler_adapter(obj,self.meth)

    def _dead(self):
        return self.obj is not None and self.obj() is None

class _href:
    """ A weakref that is always hashable. We need this
    to maintain signal maps for sender objects that might
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

class _handler_map:
    """
    _handler_map represents the signal-to-handler mapping for a
    single sender object.
    """

    def __init__(self,sender):
        self._sender = sender
        self._sigmap = {}

    def connect(self,message,handler,handler_obj=None):
        """ Add a handler for <message> """
        rh = _weak_ref_fn(handler,handler_obj)
        try:
            if rh in self._sigmap[message]:
                return
            self._sigmap[message].append(rh)
        except KeyError:
            # Message not mapped yet.
            self._sigmap[message] = [rh]
        if self._sender is not None:
            try:
                self._sender().connect_request(message)
            except AttributeError:
                pass # Ok not to implement connect_request()

    def disconnect(self,message,handler,handler_obj=None):
        """ Remove a handler for <message> """
        #print "map.disconnect:"
        rh = _weak_ref_fn(handler,handler_obj)
        try:
            self._sigmap[message].remove(rh)
        except (KeyError,ValueError):
            # Message not mapped; OK.
            pass

    def disconnect_handler_object(self,handler_obj):
        """ Remove all handlers associated with handler_obj """
        for sig in self._sigmap.keys():
            rmv = []
            for hdlr in self._sigmap[sig]:
                if hdlr.obj is handler_obj:
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

    def send_signal(self,message,sender=None,**kws):
        """ Send the given signal and associated data to all handlers. """

        # Don't try to invoke dead handlers.
        self.remove_dead_handlers(message)

        src = sender
        if src is None and self._sender is not None:
            src = self._sender()
            if src is None:
                # Sender object has been gc'd, so we shouldn't
                # be sending any signals from it!
                raise SignalException,"Sender object no longer exists"

        # Deliver the signal and associated data to all handlers.
        try:
            for hdlr in self._sigmap[message]:
                hdlr()(sender=src,message=message,**kws)
        except KeyError:
            # No handlers for the signal
            pass
        try:
            for hdlr in self._sigmap[None]:
                hdlr()(sender=src,message=message,**kws)
        except KeyError:
            # No default handlers for the signal
            pass

# The map of signal senders to handlers. Keys
# are weakref-to-sender, unless sender is None, in which case
# the sender is just None. The values are _handler_map objects.
_global_sig_map = {None:_handler_map(None)}
_sig_map_cleanup_count = 0
sig_map_cleanup_interval = 100

def remove_dead_senders():
    """ Remove handlers associated with GC'd senders.

    You should not normally have to call this function.
    """
    for src in _global_sig_map.keys():
        if src is not None:
            if src() is None:
                del _global_sig_map[src]

def get_sender_ref(sender):
    rs = None
    if sender != None:
        rs = _href(sender)
    return rs

def connect(sender,message,handler,handler_obj=None):

    """ Arrange for <handler> to be called when <sender> sends signal
    <message>. <handler> must be a callable. When <message> is sent by
    <sender> with a collection of keyword arguments, <handler> will be
    called with only the selection of supplied keyword arguments that
    it can accept. If it accepts arguments named "sender" and/or
    "message", they will be passed the signal sender and the signal
    name, respectively. Normally, that's all you need to know; the
    handler_obj argument to connect() can be ignored. If handler_obj
    is specified, it is passed as the first argument to the handler;
    this is useful in some cases described below.

    Q: What if my handler accepts different keyword arguments than
    those supplied by the signal?

    A: For example:

        class Signaller:
            def send_foo(self,data):
                signal(self,"foo_message",foo=data)
    
        class Handler:
            def handle_bar(self,bar):
                print "bar is %s"%bar
    
        s = Signaller()
        h = Handler()

    If you want to connect s's "foo_message" signal to h's handle_bar
    method, passing the signal's "foo" keyword to the handler's "bar"
    argument, you must use an adapter function and pass h as the
    handler_obj to connect:

        def adapter_func(handler,foo):
            handler.handle_bar(bar=foo)
        connect(s,"foo_message",adapter_func,h)

    The adapter_func is passed h as its first argument; this is
    somewhat like a "virtual self". (Note that using locally-defined
    functions as handlers will prohibit the handler from ever being
    unregistered (individually), since each such instance will have a
    distinct identity).

    In the case that <handler> is a bound method (and no handler_obj
    is supplied), the signal code keeps a weak rather than a strong
    reference to the associated object, so that the handler's object
    can be garbage-collected. In other words, merely having a bound
    method registered as a signal handler WILL NOT prevent an object
    from being garbage-collected; if you want to keep your handler's
    object alive, you must keep a reference to it alive yourself.

    """

    rs = get_sender_ref(sender)
    map = None
    try:
        map = _global_sig_map[rs]
    except KeyError:
        map = _handler_map(rs)
        _global_sig_map[rs] = map
    map.connect(message,handler,handler_obj)

def disconnect(sender,message,handler,handler_obj=None):
    """
    Remove all associations between <sender>'s <message> and
    the given <handler>.
    """
    rs = get_sender_ref(sender)
    map = None
    try:
        map = _global_sig_map[rs]
    except KeyError:
        # Signal not mapped; OK.
        #print "Disconnect: signal not mapped"
        return
    map.disconnect(message,handler,handler_obj)

def disconnect_handler_object(handler,sender=None):
    """
    Disconnect -all- signals handled by <handler>'s methods.
    If <sender> is supplied, only disconnect signals generated
    by <sender>
    """
    sender = get_sender_ref(sender)
    if sender is None:
        for src in _global_sig_map.keys():
            disconnect_handler_object(handler,src)
        return

    try:
        _global_sig_map[sender].disconnect_handler_object(handler)
    except KeyError:
        pass # Maybe this sender has no receivers.

"""
signal_stack is an ordered list of all objects that are
currently sending signals, and the signal name of each
signal call, as tuples. Each send_signal caller and
signal name are appended to the list, and then removed
when their signal has been processed.
"""
signal_stack = []

def signal(sender,message,**kws):
    """
    Send <message> from <sender> to all handlers, passing the
    <sender>, <message>, *args, and *kws intact.
    """

    global signal_stack
    signal_stack.append((sender,message))

    try:
        global _sig_map_cleanup_count
        _sig_map_cleanup_count += 1
        if _sig_map_cleanup_count >= sig_map_cleanup_interval:
            remove_dead_senders()
            _sig_map_cleanup_count = 0
        
        rs = get_sender_ref(sender)
        try:
            map = _global_sig_map[rs]
            map.send_signal(message,**kws)
        except KeyError:
            # Signal not mapped; OK.
            pass
    
        # Now send to default handlers (unless we already did so).
        if rs is not None:
            map = _global_sig_map[None]
            map.send_signal(message,sender=rs(),**kws)
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
    "set_state" with sender m will be sent, with a
    keyword argument args=(<state>);
    and whenever m.affinity = <value> is called,
    a signal "affinity" will be sent with sender "m"
    and keyword argument new_value=<value>.
    """

    def __init__(self,obj,siglist):
        self.__obj = obj
        self.__siglist = siglist

    def __getattr__(self,attr):
        #print "getattr %s"%attr
        if attr in ['_SignalAdapter__obj','_SignalAdapter__siglist']:
            return self.__dict__[attr]
        if attr in self.__siglist:
            meth = getattr(self.__obj,attr)
            ca = _call_adapter(self,meth,attr)
            return ca
        else:
            return getattr(self.__obj,attr)

    def __setattr__(self,attr,value):
        #print "setattr %s %s"%(attr,value)
        if attr in ['_SignalAdapter__obj','_SignalAdapter__siglist']:
            self.__dict__[attr] = value
            return
        setattr(self.__obj,attr,value)
        if attr in self.__siglist:
            signal(self,attr,new_value=value)
