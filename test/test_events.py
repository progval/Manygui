"""
>>> from anygui.Events import *
>>> class Test:
...     def handle(self, event):
...         print 'Handled!'
...

Basic functionality:

>>> s = Test()
>>> q = Test()
>>> connect(Event(source=s), q.handle, weak=1)
>>> dispatch(Event(source=s))
Handled!

>>> t = Test()
>>> evt1 = Event()
>>> evt1.type = 'something'
>>> connect(evt1, t.handle, weak=1)
>>> evt2 = Event()
>>> evt2.type = 'something'
>>> dispatch(evt2)
Handled!

[More comparison demonstrations?]

Disconnecting:

>>> t = Test()
>>> connect(Event(), t.handle, weak=1)
>>> dispatch(Event())
Handled!
>>> disconnect(Event(), t.handle)
>>> dispatch(Event())
>>>

Weak handlers:

>>> t = Test()
>>> connect(Event(), t.handle, weak=1)
>>> dispatch(Event())
Handled!
>>> del t
>>> dispatch(Event())
>>>

Strong handlers:

>>> t = Test()
>>> connect(Event(type='strong-handlers'), t.handle)
>>> del t
>>> dispatch(Event(type='strong-handlers'))
Handled!

Weak sources:

[Untestable...?]

Loop blocking:

>>> t = Test()
>>> s = Test()
>>> connect(Event(), t.handle, weak=1)
>>> dispatch(Event(source=s))
Handled!
>>> dispatch(Event(source=t))
>>> disconnect(Event(), t.handle)

Wrapper functions:

>>> def wrapper_test(obj, event):
...     print '<wrapper>'
...     obj.handle(None)
...     print '</wrapper>'
...
>>> connect(Event(type='wrapper-event'), (t, wrapper_test), weak=1)
>>> dispatch(Event(type='wrapper-event'))
<wrapper>
Handled!
</wrapper>

Return values from event handlers:

>>> def handler1(event): return 1
...
>>> def handler2(event): return 2
...
>>> def handler3(event): return 3
...
>>> evt = Event(type='return-values')
>>> connect(evt, handler1)
>>> connect(evt, handler2)
>>> connect(evt, handler3)
>>> dispatch(evt)
[1, 2, 3]

[Other API functions]

[Exceptions in handlers]

"""

if __name__ == "__main__":
    print "If you want detailed output, use \"python test_events.py -v\"."
    print "No output after this line indicates success."
    import doctest, test_events
    doctest.testmod(test_events)
