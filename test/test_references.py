"""
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
'test'

Reference callbacks:

>>> o = Object()
>>> def cb1(obj, ref):
...     print 'This is callback 1'
...
>>> def cb2(obj, ref):
...     print 'This is callback 2'
...
>>> r = ref(o, weak=1)
>>> r.callbacks.append(cb1)
>>> r.callbacks.append(cb2)
>>> del o
This is callback 1
This is callback 2

[Insert CallableReference callback tests]

CallableReference:

>>> def func1(x):
...     print x
>>> class Test:
...     def func2(self):
...         print self
...     def __repr__(self):
...         return '<Test>'
...     def __call__(self, x):
...         print x
...
>>> test = Test()
>>> sc1 = ref(func1, weak=0)
>>> wc1 = ref(func1, weak=1)
>>> sc2 = ref(Test.func2, weak=0)
>>> wc2 = ref(Test.func2, weak=1)
>>> sc3 = ref(test.func2, weak=0)
>>> wc3 = ref(test.func2, weak=1)
>>> sc4 = ref(test, weak=0)
>>> wc4 = ref(test, weak=1)
>>> sc5 = ref((test, test.func2), weak=0)
>>> wc5 = ref((test, test.func2), weak=1)
>>> sc6 = ref((test, Test.func2), weak=0)
>>> wc6 = ref((test, Test.func2), weak=1)
>>> sc1==wc1, sc2==wc2, sc3==wc3, sc4==wc4, sc5==wc5, sc6==wc6
(1, 1, 1, 1, 1, 1)

>>> sc1()('Hello, world!')
Hello, world!
>>> wc1()('Hello, world!')
Hello, world!
>>> sc2()('Hello, world!')
Hello, world!
>>> wc2()('Hello, world!')
Hello, world!
>>> sc3()()
<Test>
>>> wc3()()
<Test>
>>> sc4()('Hello, world!')
Hello, world!
>>> wc4()('Hello, world!')
Hello, world!
>>> sc5()()
<Test>
>>> wc5()()
<Test>
>>> sc6()()
<Test>
>>> wc6()()
<Test>

>>> del func1, Test, test, sc1, sc2, sc3, sc4, sc5, sc6
>>> wc2(), wc3(), wc4(), wc5(), wc6()
(None, None, None, None, None)

The global function will not die:

>>> from sys import getrefcount
>>> getrefcount(wc1()) > 0
1

[Insert RefKeyDictionary tests]

[Insert RefValueList tests]

"""

if __name__ == "__main__":
    print "If you want detailed output, use \"python test_references.py -v\"."
    print "No output after this line indicates success."
    import doctest, test_references
    doctest.testmod(test_references)
