'''
>>> from anygui.Events import *
>>> class Test:
...     def handle(self, event):
...         print 'Handled!'
...
>>> t = Test()
>>> evt = Event()
>>> evt.type = 'something'
>>> connect(evt, t.handle)
>>> dispatch(evt)
Handled!
>>> del t
>>> dispatch(evt)
>>>
'''

if __name__ == "__main__":
    print "If you want detailed output, use \"python test_messages.py -v\"."
    print "No output after this line indicates success."
    import doctest, test_events
    doctest.testmod(test_events)
