
class IllegalState(Exception): pass
class CannotCalculate(Exception): pass
class ValueUnchanged(Exception): pass

class EquivalencePartition:

    def __init__(self):
        self.classes = {}

    def equate(self, a, b):
        class_a = self.classes.get(a, {a:1})
        class_b = self.classes.get(b, {b:1})
        class_a.update(class_b)
        for key in class_a.keys():
            self.classes[key] = class_a

    def getClass(self, key):
        return self.classes[key]        

    def getClasses(self):
        done = {}
        result = []
        for c in self.classes.values():
            keys = c.keys()
            keys.sort()
            keys = tuple(keys)
            if not done.has_key(keys):
                done[keys] = 1
                result.append(c)
        return result

    def equal(self, a, b):
        return self.classes[a] == self.classes[b]

class RuleEngine:
    
    def __init__(self):
        self.equiv = EquivalencePartition()
        self.sizes = {}

    def define(self, rule):
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

    def check(self, state, defs): # Ahem... I'll clean this code up in a while ;) [mlh]
        defs = defs[:]
        for c in self.equiv.getClasses():
            for key in defs:
                if c.has_key(key):
                    defs.remove(key)
                    break
            else:
                if c:
                    k, v = c.popitem()
                    value = self.getValue(state, k)
                    while 1:
                        try: k, v = c.popitem()
                        except KeyError: break
                        if value != self.getValue(state, k):
                            raise IllegalState

    def sync(self, state, defs):
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
