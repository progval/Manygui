from unittest import TestCase, main
from anygui.Rules import RuleEngine, IllegalState

# TODO: Test the addition of undefined values (that are not present
# when sync is called)
# Check that defs that are not in state raise IllegalState

class RectangleTestCase(TestCase):
    def __init__(self, *args, **kwds):
        TestCase.__init__(self, *args, **kwds)
        self.eng = RuleEngine()
        self.eng.define('position = x, y')
        self.eng.define('size = width, height')
        self.eng.define('geometry = x, y, width, height')
        state = self.state_init = {}
        state['x'] = 10
        state['y'] = 10
        state['width'] = 9999
        state['height'] = 9999
        state['size'] = 9999, 9999
        state['position'] = 10, 10
        state['geometry'] = 10, 10, 9999, 9999

    def setUp(self):
        self.state = self.state_init.copy()

    def checkState(self, x, y, width, height):
        state = self.state
        self.assertEqual(state['x'], x)
        self.assertEqual(state['y'], y)
        self.assertEqual(state['position'][0], x)
        self.assertEqual(state['position'][1], y)
        self.assertEqual(state['width'], width)
        self.assertEqual(state['height'], height)
        self.assertEqual(state['size'][0], width)
        self.assertEqual(state['size'][1], height)
        self.assertEqual(state['geometry'][0], x)
        self.assertEqual(state['geometry'][1], y)
        self.assertEqual(state['geometry'][2], width)
        self.assertEqual(state['geometry'][3], height)

    def testX(self):
        "Setting x and syncing with ['x']"
        state = self.state
        state['x'] = 20
        self.eng.sync(state, ['x'])
        self.checkState(20, 10, 9999, 9999)

    def testY(self):
        "Setting y and syncing with ['y']"
        state = self.state
        state['y'] = 20
        self.eng.sync(state, ['y'])
        self.checkState(10, 20, 9999, 9999)

    def testPosition(self):
        "Setting position and syncing with ['position']"
        state = self.state
        state['position'] = 20, 20
        self.eng.sync(state, ['position'])
        self.checkState(20, 20, 9999, 9999)

    def testGeometry(self):
        "Setting geometry and syncing with ['geometry']"
        state = self.state
        state['geometry'] = 42, 42, 42, 42
        self.eng.sync(state, ['geometry'])
        self.checkState(42, 42, 42, 42)

    def testLegalEmptySync(self):
        "Syncing a consistent state with []"
        state = self.state
        self.eng.sync(state, [])
        self.checkState(10, 10, 9999, 9999)

    def genericIllegalEmptySyncTest(self, name, value):
        state = self.state.copy()
        state[name] = value
        self.assertRaises(IllegalState, self.eng.sync, state, [])

    def testIllegalEmptySync(self):
        "Syncing an inconsistent state with []"

        # Generalize...
        self.genericIllegalEmptySyncTest('x', 0)
        self.genericIllegalEmptySyncTest('y', 0)
        self.genericIllegalEmptySyncTest('width', 0)
        self.genericIllegalEmptySyncTest('height', 0)
        self.genericIllegalEmptySyncTest('position', (0, 10))
        self.genericIllegalEmptySyncTest('position', (10, 0))
        self.genericIllegalEmptySyncTest('size', (0, 10))
        self.genericIllegalEmptySyncTest('size', (10, 0))
        for i in xrange(4):
            v = [10, 10, 9999, 9999]
            v[i] = 0
            self.genericIllegalEmptySyncTest('geometry', v)

    def testInconsistentSyncList(self):
        "Syncing on two inconsistent, related values"
        state = self.state
        
        # Generalize...
        state['x'] = 42
        state['position'] = 20, 30
        self.assertRaises(IllegalState, self.eng.sync, state, ['x', 'position'])

    def testConsistentSyncList(self):
        "Syncing on two consistent, related values"
        state = self.state
        
        # Generalize...
        state['x'] = 42
        state['position'] = 42, 10
        self.eng.sync(state, ['x', 'position'])
        self.checkState(42, 10, 9999, 9999)

    def testIndependentSyncList(self):
        "Syncing on two independent values"
        state = self.state
        
        # Generalize...
        state['position'] = 42, 42
        state['size'] = 42, 42
        self.eng.sync(state, ['position', 'size'])
        self.checkState(42, 42, 42, 42)

if __name__ == '__main__': main()
