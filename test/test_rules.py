from unittest import TestCase, main
from anygui.Rules import RuleEngine, IllegalState

class RectangleTestCase(TestCase):
    def setUp(self):
        self.eng = RuleEngine()

        # FIXME: Is this rule set complete? Is it minimal?
        self.eng.addRule('position = x, y')
        self.eng.addRule('x = position[0]')
        self.eng.addRule('y = position[1]')
        self.eng.addRule('size = width, height')
        self.eng.addRule('width = size[0]')
        self.eng.addRule('height = size[1]')
        self.eng.addRule('geometry = position + size')
        self.eng.addRule('geometry = x, y, width, height')
        self.eng.addRule('position = geometry[0], geometry[1]')
        self.eng.addRule('size = geometry[2], geometry[3]')

        # How can this be calculated automatically? (Transitive
        # closure etc. won't work directly...)
        self.eng.setAffected('x', ['position', 'geometry'])
        self.eng.setAffected('y', ['position', 'geometry'])
        self.eng.setAffected('position', ['x', 'y', 'geometry'])
        self.eng.setAffected('width', ['size', 'geometry'])
        self.eng.setAffected('height', ['size', 'geometry'])
        self.eng.setAffected('size', ['width', 'height', 'geometry'])
        self.eng.setAffected('geometry', ['x', 'y', 'width', 'height', 'position', 'size'])

    def testMisc(self): # FIXME: Rewrite as more specific test cases...

        vals = {}
        vals['x'] = 10
        vals['y'] = 20
        vals['width'] = 9999
        vals['height'] = 9999
        vals['size'] = 9999, 9999
        vals['position'] = 10, 10
        vals['geometry'] = 10, 10, 9999, 9999

        self.assertEqual(self.eng.adjust(vals, ['y']), [])

        self.assertEqual(vals['position'], (10, 20))
        self.assertEqual(vals['geometry'], (10, 20, 9999, 9999))
        
        vals['position'] = 42, 42
        self.assertEqual(self.eng.adjust(vals, ['position']), [])
        self.assertEqual(vals['x'], 42)
        self.assertEqual(vals['y'], 42)
        self.assertEqual(vals['geometry'], (42, 42, 9999, 9999))

        vals['geometry'] = 1, 2, 3, 4
        self.assertEqual(self.eng.adjust(vals, ['geometry']), [])

        self.assertEqual(vals['x'], 1)
        self.assertEqual(vals['y'], 2)
        self.assertEqual(vals['width'], 3)
        self.assertEqual(vals['height'], 4)
        self.assertEqual(vals['position'], (1, 2))
        self.assertEqual(vals['size'], (3, 4))

        # If the "illegal state" actually checked the expression and the
        # values etc. (no change), this shouldn't raise an exception...
        # This behaviour may change (to become more intelligent ;)
        self.assertRaises(IllegalState, self.eng.adjust, vals, ['x', 'position'])

if __name__ == '__main__': main()
