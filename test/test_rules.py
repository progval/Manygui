from unittest import TestCase, main
from anygui.Rules import AggregateRuleEngine

class RectangleTestCase(TestCase):
    def setUp(self):
        self.eng = AggregateRuleEngine()
        self.eng.define('position = x, y')
        self.eng.define('size = width, height')
        self.eng.define('geometry = x, y, width, height')

    def testMisc(self): # FIXME: Rewrite as more specific test cases...

        state = {}
        state['x'] = 10
        state['y'] = 20
        state['width'] = 9999
        state['height'] = 9999
        state['size'] = 9999, 9999
        state['position'] = 10, 10
        state['geometry'] = 10, 10, 9999, 9999

        self.assertEqual(self.eng.sync(state, ['y']), [])

        self.assertEqual(state['position'], (10, 20))
        self.assertEqual(state['geometry'], (10, 20, 9999, 9999))

        state['position'] = 42, 42
        self.assertEqual(self.eng.sync(state, ['position']), [])
        self.assertEqual(state['x'], 42)
        self.assertEqual(state['y'], 42)
        self.assertEqual(state['geometry'], (42, 42, 9999, 9999))

        state['geometry'] = 1, 2, 3, 4
        self.assertEqual(self.eng.sync(state, ['geometry']), [])

        self.assertEqual(state['x'], 1)
        self.assertEqual(state['y'], 2)
        self.assertEqual(state['width'], 3)
        self.assertEqual(state['height'], 4)
        self.assertEqual(state['position'], (1, 2))
        self.assertEqual(state['size'], (3, 4))

if __name__ == '__main__': main()
