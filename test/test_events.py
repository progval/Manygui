"""
>>> from anygui.Events import *
>>> class Test:
...     def handle(self, event):
...         print 'Handled!'
...

Basic functionality:

>>> s = Test()
>>> q = Test()
>>> link(s, q.handle, weak=1)
>>> send(s)
Handled!

>>> t = Test()
>>> evt1 = Event()
>>> evt1.type = 'something'
>>> link(event='something', t.handle, weak=1)
>>> send(event='something')
Handled!

[More comparison demonstrations?]

Disconnecting:

>>> t = Test()
>>> link(handler=t.handle, weak=1)
>>> send()
Handled!
>>> unlink(handler=t.handle)
>>> send()
>>>

Weak handlers:

>>> t = Test()
>>> link(handler=t.handle, weak=1)
>>> send()
Handled!
>>> del t
>>> send()
>>>

Strong handlers:

>>> t = Test()
>>> link(event='strong-handlers'), handler=t.handle)
>>> del t
>>> send(event='strong-handlers')
Handled!

Weak sources:

[Untestable...?]

Loop blocking:

>>> t = Test()
>>> s = Test()
>>> link(handler=t.handle, weak=1)
>>> send(s)
Handled!
>>> send(t)
>>> unlink(handler=t.handle)

Wrapper functions:

>>> def wrapper_test(obj, event):
...     print '<wrapper>'
...     obj.handle(None)
...     print '</wrapper>'
...
>>> link(event='wrapper-event', handler=(t, wrapper_test), weak=1)
>>> send(event='wrapper-event')
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
>>> link(event='return-values', handler=handler1)
>>> link(event='return-values', handler=handler2)
>>> link(event='return-values', handler=handler3)
>>> send(event='return-values')
[1, 2, 3]

[Other API functions]

[Exceptions in handlers]

"""

if __name__ == "__main__":
    print "If you want detailed output, use \"python test_events.py -v\"."
    print "No output after this line indicates success."
    import doctest, test_events
    doctest.testmod(test_events)
