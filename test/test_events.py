"""
>>> from anygui.Events import *
>>> class Test:
...     def handle(self, **kw):
...         print 'Handled!'
...

Basic functionality:

>>> s = Test()
>>> q = Test()
>>> link(s, 'default', q.handle)
>>> send(s, 'default')
Handled!
>>> unlink(s, 'default', q.handle)
>>> send(s, 'default')

>>> link(s, q.handle)
>>> send(s)
Handled!
>>> unlink(s, q.handle)
>>> send(s)

#>>> t = Test()
#>>> evt1 = Event()
#>>> evt1.type = 'something'
#>>> link(event='something', t.handle, weak=1)
#>>> send(event='something')
Handled!

[More comparison demonstrations?]

Weak handlers:

>>> s = Test()
>>> t = Test()
>>> link(s, t.handle, weak=1)
>>> send(s)
Handled!
>>> del t
>>> send(s)
>>>

Strong handlers:

>>> s = Test()
>>> t = Test()
>>> link(s, 'strong-handlers', t.handle)
>>> del t
>>> send(s, 'strong-handlers')
Handled!

Weak sources:

[Untestable...?]

Loop blocking:

>>> s = Test()
>>> t = Test()
>>> link(s, t.handle)
>>> link(t, t.handle)
>>> send(s)
Handled!
>>> send(t)

Wrapper functions:

>>> def wrapper_test(obj, **kw):
...     print '<wrapper>'
...     obj.handle()
...     print '</wrapper>'
...
>>> s = Test()
>>> t = Test()
>>> link(s, 'wrapper-event', (t, wrapper_test))
>>> send(s, 'wrapper-event')
<wrapper>
Handled!
</wrapper>

Return values from event handlers:

>>> s = Test()
>>> def handler1(**kw): return 1
...
>>> def handler2(**kw): return 2
...
>>> def handler3(**kw): return 3
...
>>> link(s, 'return-values', handler1)
>>> link(s, 'return-values', handler2)
>>> link(s, 'return-values', handler3)
>>> send(s, 'return-values')
[1, 2, 3]

[Tag handling]

[Other API functions]

[Exceptions in handlers]

"""

if __name__ == "__main__":
    print "If you want detailed output, use \"python test_events.py -v\"."
    print "No output after this line indicates success."
    import doctest, test_events
    doctest.testmod(test_events)
