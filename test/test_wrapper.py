
from unittest import TestCase, main

# FIXME: Does not test partial ordering of setters (not yet implemented)

# Temporary:
import warnings
warnings.filterwarnings('ignore')

class Stub:
    def dummyMethod(*args, **kwds):
        return Stub()
    def __getattr__(self, name):
        return dummyMethod
    def __setattr__(self, name, value):
        pass
    def __getitem__(self, key):
        return Stub()
                    
from anygui.Wrappers import AbstractWrapper

class TestWrapperWithAggregates(AbstractWrapper):
    def setPosition(self, x, y):
        pass
    def setSize(self, width, height):
        pass
    def setGeometry(self, x, y, width, height):
        pass
    def setX(self, x):
        pass
    def setY(self, y):
        pass
    def setWidth(self, width):
        pass
    def setHeight(self, height):
        pass
    def setText(self, text):
        pass

class TestWrapperWithoutAggregates(AbstractWrapper):
    
    def setX(self, x):
        pass
    def setY(self, y):
        pass
    def setWidth(self, width):
        pass
    def setHeight(self, height):
        pass
    def setText(self, text):
        pass

class WrapperWithAggregatesTestCase(TestCase):

    def setUp(self):
        self.wrapper = TestWrapperWithAggregates(Stub(), _test=1)

    def genericAggregateTest(self, settername, attrs):
        s, u = self.wrapper.getSetters(attrs)
        self.failUnless(len(u) == 0, 'There should be no unhandled attributes')
        self.failUnless(len(s) == 1, 'Exactly one setter should be returned')
        self.failUnless(s[0][0].__name__ == settername, 'The setter should '+settername+'()')
        self.failUnless(len(s[0][1]) == len(attrs), 'The setter should cover '+repr(len(attrs))+' attributes')
        for attr in attrs:
            self.failUnless(attr in s[0][1], attr + ' should be covered')

    def testGetSetters1(self):
        'Test default aggregate position == (x, y)'
        self.genericAggregateTest('setPosition', ['x', 'y'])
        
    def testGetSetters2(self):
        'Test default aggregate size == (width, height)'
        self.genericAggregateTest('setSize', ['width', 'height'])

    def testGetSetters3(self):
        'Test default aggregate geometry == (x, y, width, height)'
        self.genericAggregateTest('setGeometry', ['x', 'y', 'width', 'height'])

    def testGetSetters4(self):
        'Test geometry with attributes in scrambled order'
        self.genericAggregateTest('setGeometry', ['height', 'x', 'width', 'y'])

    def testGetSetters5(self):
        'Test for unknown attributes'
        s, u = self.wrapper.getSetters(['unknown1', 'unknown2', 'unknown3'])
        self.failUnless(len(s) == 0, 'No unknown attributes should be handled')
        self.failUnless(len(u) == 3, 'Unknown attributes should be returned as such')

    def testGetSetters6(self):
        'Test for known and unknown attributes in combination'
        s, u = self.wrapper.getSetters(['x', 'y', 'width', 'unknown'])
        self.failUnless(len(s) == 2, 'Should have setters for (x, y) and width')
        self.failUnless(len(u) == 1, 'Should not handle unknown')

    def testGetSetters7(self):
        'Test for non-aggregate setter'
        s, u = self.wrapper.getSetters(['x'])
        self.failUnless(s[0][0].__name__ == 'setX', 'Handler should be setX()')

class WrapperWithoutAggregatesTestCase(TestCase):

    def setUp(self):
        self.wrapper = TestWrapperWithoutAggregates(Stub(), _test=1)

    def genericAggregateTest(self, attrs):
        s, u = self.wrapper.getSetters(attrs)
        self.failUnless(len(u) == 0, 'There should be no unhandled attributes')
        self.failUnless(len(s) == len(attrs), 'Exactly ' + repr(len(attrs)) + 'setters should be returned')
        handled_attrs = []
        for x in s:
            self.failUnless(len(x[1]) == 1, 'There should be no aggregates')
            handled_attrs.append(x[1][0])
        for attr in attrs:
            self.failUnless(attr in handled_attrs, attr + ' should be handled')

    def testGetSetters1(self):
        'Test for nonexistent aggregate position == (x, y)'
        self.genericAggregateTest(['x', 'y'])

class UpdateTestWrapper(AbstractWrapper):

    def __init__(self, proxy):
        AbstractWrapper.__init__(self, proxy, _test=1)
        self.reset()

    def reset(self):
        self.called = []

    def register(self, name, *args):
        self.called.append(name + '(' + ', '.join(map(repr, args)) + ')')

    def setX(self, x):
        self.register('setX', x)

    def setY(self, y):
        self.register('setY', y)

    def setPosition(self, x, y):
        self.register('setPosition', x, y)

    def setWidth(self, width):
        self.register('setWidth', width)

    def setHeight(self, height):
        self.register('setHeight', height)

    def setSize(self, width, height):
        self.register('setSize', width, height)

    def setGeometry(self, x, y, width, height):
        self.register('setGeometry', x, y, width, height)

    def setText(self, text):
        self.register('setText', text)

class UpdateTestCase(TestCase):

    def setUp(self):
        self.wrapper = UpdateTestWrapper(Stub())

    def genericUpdateTest(self, state, testCalled):
        self.wrapper.push(state)
        called = self.wrapper.called
        called.sort()
        self.assertEqual(called, testCalled)
        self.wrapper.reset()

    def testUpdate1(self):
        'Test update without aggregates'
        self.genericUpdateTest(
            {
            'x': 1,
            'width': 10,
            'text': 'Hello'
            },
            [
            "setText('Hello')",
            'setWidth(10)',
            'setX(1)'
            ])

    def testUpdate2(self):
        'Test update with position == (x, y)'
        self.genericUpdateTest(
            {
            'x': 1,
            'y': 2,
            },
            [
            'setPosition(1, 2)'
            ])

    def testUpdate3(self):
        'Test update with size == (width, height)'
        self.genericUpdateTest(
            {
            'width': 10,
            'height': 20
            },
            [
            'setSize(10, 20)'
            ])

    def testUpdate4(self):
        'Test update with geometry == (x, y, width, height)'
        self.genericUpdateTest(
            {
            'x': 1,
            'y': 2,
            'width': 10,
            'height': 20
            },
            [
            'setGeometry(1, 2, 10, 20)'
            ])
        
    def testUpdate5(self):
        'Test update with aggregates and non-aggregates'
        self.genericUpdateTest(
            {
            'x': 1,
            'y': 2,
            'height': 50,
            'text': 'Hello'
            },
            [
            'setHeight(50)',
            'setPosition(1, 2)',
            "setText('Hello')"
            ])

    def testUpdate6(self):
        'Test update with unknown attributes'        
        self.genericUpdateTest(
            {
            'foobar': 42,
            'babar': 'Fnord'
            },
            [
            ])

    def testUpdate7(self):
        'Test update with known and unknown attributes'
        self.genericUpdateTest(
            {
            'x': 1,
            'y': 2,
            'height': 50,
            'text': 'Hello',
            'foobar': 42
            },
            [
            'setHeight(50)',
            'setPosition(1, 2)',
            "setText('Hello')"
            ])

if __name__ == '__main__': main()


