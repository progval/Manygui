
raise "Don't use this module!"

class IllegalState(Exception): pass

class RuleEngine:

    def call(self, name, check=0):
        try:
            method = getattr(self, 'sync'+name.capitalize())
            method(check)
        except (AttributeError, TypeError): pass

    def sync(self, obj, defs):
        self.obj = obj
        self.state = obj.state
        self.defs = defs
        self.complete()
        for name in defs:
            self.call(name)
        for name in self.atoms:
            self.call(name, check=1)

    def wholeSync(self, name, *parts):
        state = self.state
        this = state[name]
        for attr, index in parts:
            other = state[attr]
            if this != other[index]:
                if attr in self.defs: raise IllegalState, 'overdetermined sync'
                other = list(other)
                other[index] = this
                other = tuple(other)
                self.obj.rawModify(**{attr:other})

    def wholeCheck(self, name, *parts):
        state = self.state
        this = state[name]
        for attr, index in parts:
            other = state[attr]
            if this != other[index]: raise IllegalState, 'underdetermined sync'

    def partSync(self, name, *parts):
        state = self.state
        this = state[name]
        modified = []
        for attr, index in parts:
            other = state[attr]
            if this[index] != other:
                if attr in self.defs: raise IllegalState, 'overdetermined sync'
                self.obj.rawModify(**{attr:this[index]})
                modified.append(attr)
        return modified

class RectEngine(RuleEngine):

    atoms = 'x', 'y', 'width', 'height'

    def complete(self):
        # x, y, width, and height are assumed to exist
        state = self.state
        if not state.has_key('position'):
            state['position'] = state['x'], state['y']
        if not state.has_key('size'):
            state['size'] = state['width'], state['height']
        if not state.has_key('geometry'):
            state['geometry'] = state['x'], state['y'], \
                                state['width'], state['height']

    def syncX(self, check=0):
        if check: method = self.wholeCheck
        else: method = self.wholeSync
        method('x', ('position', 0), ('geometry', 0))

    def syncY(self, check=0):
        if check: method = self.wholeCheck
        else: method = self.wholeSync
        method('y', ('position', 1), ('geometry', 1))

    def syncWidth(self, check=0):
        if check: method = self.wholeCheck
        else: method = self.wholeSync
        method('width', ('size', 0), ('geometry', 2))

    def syncHeight(self, check=0):
        if check: method = self.wholeCheck
        else: method = self.wholeSync
        method('height', ('size', 1), ('geometry', 3))

    def syncPosition(self, dummy=0):
        modified = self.partSync('position', ('x', 0), ('y', 1))
        for name in modified: self.call(name)

    def syncSize(self, dummy=0):
        modified = self.partSync('size', ('width', 0), ('height', 1))
        for name in modified: self.call(name)

    def syncGeometry(self, dummy=0):
        modified = self.partSync('geometry', ('x', 0), ('y', 1),
                                 ('width', 2), ('height', 3))
        for name in modified: self.call(name)


















  

'''
class IllegalState(Exception): pass
class CannotCalculate(Exception): pass
class ValueUnchanged(Exception): pass
class Undefined: pass
Undefined = Undefined()

class EquivalencePartition:
    """
    A partition of a set into equivalence classes.

    Each class is represented as a dictionary mapping the euivalent
    objects to a true value.
    """
    def __init__(self):
        self.classes = {}

    def equate(self, a, b):
        """
        Assert that a and b belong to the same equivalence class.
        """
        class_a = self.classes.get(a, {a:1})
        class_b = self.classes.get(b, {b:1})
        class_a.update(class_b)
        for key in class_a.keys():
            self.classes[key] = class_a

    def getClass(self, key):
        """
        Get (a copy of) the class that key belongs to (as a dictionary).
        """
        return self.classes[key].copy()

    def getClasses(self):
        """
        Get (copies of) all the equivalence classes (as a list of
        dictionaries).
        """
        done = {}
        result = []
        for c in self.classes.values():
            keys = c.keys()
            keys.sort()
            keys = tuple(keys)
            if not done.has_key(keys):
                done[keys] = 1
                result.append(c.copy())
        return result

# TODO: Clean up the code a bit [mlh20020430]
class RuleEngine:
    """
    A rule engine enforcing the equivalence relation of an
    EquivalencePartition.

    The engine is designed to deal with atomic and aggregate values
    where the aggregates are sequences consisting of atomics.
    """
    def __init__(self):
        self.equiv = EquivalencePartition()
        self.sizes = {}

    def complete(self, state):
        """
        Adds placeholder values for missing names covered by the
        engine. These placeholder values should eventually be removed by
        sync.
        """
        for name, size in self.sizes.items():
            try: state[name]
            except KeyError:
                if size == 1: state[name] = Undefined
                else:
                    state[name] = [Undefined]*size

    def getMissing(self, state):
        """
        Returns the elements that are covered by the rules but which
        are missing from the state. These elements are returned as a
        dictionary with tuples of the form (aggregate, index) or
        (atom, None) as keys and 1 as values.
        """
        result = {}
        for name, size in self.sizes.items():
            try: state[name]
            except KeyError:
                if size == 1: result[(name, None)] = 1
                else:
                    for i in xrange(size):
                        result[(name, i)] = 1
        return result

    def define(self, rule):
        """
        Assert an equation of the form x = y, z, w.

        This will add the tuples ('x', 0) and ('y', None') to the same
        equivalence class, ('x', 1) and ('z', None) to another,
        etc. The second element of these tuples is the index that
        indicates which part of an aggregate is referred to (with None
        for atomic values).
        """
        whole, parts = rule.split('=')
        whole = whole.strip()
        pos = 0
        for part in parts.split(','):
            part = part.strip()
            self.sizes[part] = None
            a = (whole, pos)
            b = (part, None)
            self.equiv.equate(a, b)
            pos += 1
        self.sizes[whole] = pos

    def explode(self, names):
        result = []
        for name in names:
            try: size = self.sizes[name]
            except KeyError: continue
            if size is None:
                result.append((name, None))
            else:
                for i in xrange(self.sizes[name]):
                    result.append((name, i))
        return result

    def getValue(self, state, key):
        name, index = key
        if index is None: return state[name]
        else: return state[name][index]

    def setValue(self, state, key, value):
        name, index = key
        if index is None: state[name] = value
        else:
            state[name] = list(state[name])
            state[name][index] = value

    def getUndefs(self, state, defs):
        undefs = {}
        for key in defs:
            value = self.getValue(state, key)
            c = self.equiv.getClass(key)
            for other in c.keys():
                if self.getValue(state, other) != value:
                    undefs[other] = 1
        for key in defs:
            if undefs.has_key(key): raise IllegalState
        return undefs

    def check(self, state, defs):
        defs = defs[:]
        for c in self.equiv.getClasses():
            for key in defs:
                if c.has_key(key):
                    defs.remove(key)
                    break
            else:
                if c:
                    value = Undefined
                    while 1:
                        try: k, v = c.popitem()
                        except KeyError: break
                        try: value = self.getValue(state, k)
                        except KeyError: pass
                    if value is not Undefined:
                        while 1:
                            try: k, v = c.popitem()
                            except KeyError: break
                            try:
                                if value != self.getValue(state, k):
                                    raise IllegalState
                            except KeyError: pass

    def sync(self, state, defs):
        """
        Sync a given state dictionary according to the defined rules.

        The components of the state dictionary are alle synced with
        the other elements in the same equivalence class. This syncing
        can take one of three forms (for each equivalence class):

          1. If none of the elements of the defs list is part of the
             equivalence class, simply check that all elements of the
             class are equal; if they're not, raise an IllegalState
             exception.

          2. If one of the elements of the defs list is part of the
             equivalence class, modify all the others so they are
             equal to this element.

          3. If more than one element of the defs list are part of the
             equivalence class, check that they are all equal. If they
             are not, raise an IllegalState exception. If they are,
             modify all the others so they are equal to these
             elements.

        If a name covered by the rules is not found in the state
        dictionary, it is treated as undefined, and if a successful
        sync is performed, the name will be given a value.

        One important property of the sync method is that it (unlike
        define) does not alter the state of the RuleEngine.
        """
        defs = self.explode(defs)
        self.complete(state)
        undefs = self.getUndefs(state, defs)
        # FIXME: Check whether defs contains one of the missing values...
        missing = self.getMissing(state)
        undefs.update(missing)
        # FIXME: Add values to the defs to get the missing defined
        for m in missing.keys():
            c = self.equiv.getClass(m)
            for other in c.keys():
                
        reps = self.getRepresentatives
        self.check(state, defs)
        stable = 0
        while undefs and not stable:
            stable = 1
            for key in undefs.keys():
                try: newValue = self.newValue(key, state, undefs)
                except (CannotCalculate, ValueUnchanged): pass
                else:
                    self.setValue(state, key, newValue)
                    del undefs[key]
                    stable = 0
        assert not undefs
        
    def newValue(self, key, state, undefs):
        oldValue = self.getValue(state, key)
        for other in self.equiv.getClass(key).keys():
            if not undefs.has_key(other):
                newValue = self.getValue(state, other)
                if newValue is not Undefined: break
        else:
            raise CannotCalculate
        if oldValue == newValue: raise ValueUnchanged
        return newValue
'''
