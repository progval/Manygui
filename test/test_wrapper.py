
from unittest import TestCase, main

# TODO: Add tests for add tests for update(); add tests for wrappers
# without setters.

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

class TestWrapperWithSetters(AbstractWrapper):
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

class TestWrapperWithoutSetters(AbstractWrapper):
    pass

class WrapperWithSettersTestCase(TestCase):

    def setUp(self):
        self.wrapper = TestWrapperWithSetters(Stub())

    def genericAggregateTest(self, settername, attrs):
        s, u = self.wrapper.getSetters(attrs)
        self.failUnless(len(u) == 0, 'There should be no unhandled attributes')
        self.failUnless(len(s) == 1, 'Exactly one setter should be returned')
        self.failUnless(s[0][0].__name__ == settername, 'The setter should '+settername+'()')
        self.failUnless(len(s[0][1]) == len(attrs), 'The setter should cover '+`len(attrs)`+' attributes')
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

# class WrapperWithoutSettersTestCase(TestCase): pass

if __name__ == '__main__': main()
