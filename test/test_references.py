'''
>>> from anygui.References import *
>>> class Object:
...     def __repr__(self):
...         return '<Object>'

ref(), WeakReference and StrongReference:

>>> o1, o2 = Object(), Object()
>>> s = ref(o1, weak=0)
>>> w = ref(o2, weak=1)
>>> s() is o1
1
>>> w() is o2
1
>>> del o1, o2
>>> s()
<Object>
>>> w()
>>> o = Object()
>>> s = ref(o, weak=0)
>>> w = ref(o, weak=1)
>>> w == s
1
>>> d = {}
>>> d[w] = 'test'
>>> d[s]
'test'
>>> del o, s
>>> w()
>>> d[w]
'test'o

[callbacks]

[CallableReference]

[RefKeyDictionary]

[RefValueList]

'''

if __name__ == "__main__":
    print "If you want detailed output, use \"python test_messages.py -v\"."
    print "No output after this line indicates success."
    import doctest, test_references
    doctest.testmod(test_references)
