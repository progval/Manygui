
class IllegalState(Exception): pass
class CannotCalculate(Exception): pass
class ValueUnchanged(Exception): pass

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
            if self.sizes[name] is None:
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
                    c = c.copy()
                    k, v = c.popitem()
                    value = self.getValue(state, k)
                    while 1:
                        try: k, v = c.popitem()
                        except KeyError: break
                        if value != self.getValue(state, k):
                            raise IllegalState

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
        
        """
        defs = self.explode(defs)
        undefs = self.getUndefs(state, defs)
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
        return undefs.keys()
        
    def newValue(self, key, state, undefs):
        oldValue = self.getValue(state, key)
        for other in self.equiv.getClass(key).keys():
            if not undefs.has_key(other):
                newValue = self.getValue(state, other)
                break
        else:
            raise CannotCalculate
        if oldValue == newValue: raise ValueUnchanged
        return newValue
