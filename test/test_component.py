
from unittest import TestCase, main

# Temporary:
import warnings
warnings.filterwarnings('ignore')
                    
from anygui.Components import Component

class DummyWrapper:
    def update(self, *args, **kwds): pass

class TestComponent(Component):
    # Defaults...
    state = {
        'x': 0,
        'y': 0,
        'position': (0, 0),
        'width': 10,
        'height': 10,
        'size': (10, 10),
        'geometry': (0, 0, 10, 10)
        }
    def wrapperFactory(self): return DummyWrapper()

class InternalSyncTestCase(TestCase):
    def setUp(self):
        self.comp = TestComponent()
    def test0(self): # Move to Attrib test suite...
        'Simple attribute assignment should work'
        self.comp.x = 100
        self.assertEqual(self.comp.x, 100)
        self.comp.y = 200
        self.assertEqual(self.comp.y, 200)
        self.comp.width = 300
        self.assertEqual(self.comp.width, 300)
        self.comp.height = 400
        self.assertEqual(self.comp.height, 400)
    def test2(self):
        'position should be synchronized with x and y'
        self.comp.rawSet(x=42)
        self.comp.rawSet(y=24)
        self.comp.internalSync(['x', 'y'])
        self.assertEqual(self.comp.x, 42,
                         "internalSync shouldn't destroy assignments")
        self.assertEqual(self.comp.y, 24,
                         "internalSync shouldn't destroy assignments")
        self.assertEqual(self.comp.x,
                         self.comp.position[0],
                         'x should equal position[0]')
        self.assertEqual(self.comp.x,
                         self.comp.position[0],
                         'y should equal position[1]')

    def test3(self):
        'x and y should be synchronized with position'
        self.comp.rawSet(position=(123, 99))
        self.comp.internalSync(['position'])
        self.assertEqual(self.comp.position[0], 123,
                         "internalSync shouldn't destroy assignments")
        self.assertEqual(self.comp.position[1], 99,
                         "internalSync shouldn't destroy assignments")
        self.assertEqual(self.comp.x,
                         self.comp.position[0],
                         'x should equal position[0]')
        self.assertEqual(self.comp.x,
                         self.comp.position[0],
                         'y should equal position[1]')

    def DISABLEDtest4(self):
        'geometry should be synchronized with x, y, width, and height'
        self.comp.rawSet(x=500)
        self.comp.rawSet(y=501)
        self.comp.rawSet(width=502)
        self.comp.rawSet(height=503)
        self.comp.internalSync(['x', 'y', 'width', 'height'])
        self.assertEqual(tuple(self.comp.geometry),
                         (500, 501, 502, 503))
        

    # TODO: Add more tests...

if __name__ == '__main__': main()
