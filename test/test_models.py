from anygui import *
from anygui.Mixins import Observable
import unittest

cases = {
    "1": "[('_set_value', (1,), {})]",
    "['foo', 'bar', 'baz', 'frozzbozz']": "[('append', ('frozzbozz',), {})]",
    '"There\'s no peace at the gate"': "[('__setslice__', (5, 7, \"'\"), {})]"
}

class TestObserver:
    def model_changed(self, target=None, change=None):
        assert cases[repr(target)] == repr(change)

class ObserverTestCase(unittest.TestCase):
    def setUp(self):
        self.bm = BooleanModel(0)
        self.lm = ListModel('foo bar baz'.split())
        self.tm = TextModel('There is no peace at the gate')
        to = self.to = TestObserver()
        self.bm.add_view(to)
        self.lm.add_view(to)
        self.tm.add_view(to)

    def testBooleanModel(self):
        self.bm.value = 1

    def testListModel(self):
        self.lm.append('frozzbozz')

    def testTextModel(self):
        self.tm[5:7] = "'"

unittest.main()
