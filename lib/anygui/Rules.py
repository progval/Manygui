
class IllegalState(Exception): pass
class ValueUnchanged(Exception): pass
class CannotCalculate(Exception): pass

def addSubKey(dict, key, subkey):
    dict.setdefault(key, {})[subkey] = 1

def equiv(a, b):
    try:
        if len(a) != len(b): return 0
        for x, y in zip(a, b):
            if x != y: return 0
        return 1
    except TypeError:
        return a == b

class RuleEngine:
    
    def __init__(self):
        self.parts = {}
        self.whole = {}
        self.rules = {}

    def getChildren(self, name):
        return self.parts.get(name, {})

    def getOrderedChildren(self, name):
        return self.rules.get(name, [])

    def getParents(self, name):
        return self.whole.get(name, {})

    def getSpouses(self, name):
        result = {}
        for child in self.getChildren(name).keys():
            result.update(self.getParents(child))
        try: del result[name]
        except: pass
        return result

    def define(self, rule):
        whole, parts = rule.split('=')
        whole = whole.strip()
        rule = []
        for part in parts.split(','):
            part = part.strip()
            rule.append(part)
            addSubKey(self.whole, part, whole)
            addSubKey(self.parts, whole, part)
        self.rules[whole] = rule

    def check(self, state, names, undef):
        for name in names:
            try: newValue = self.newValue(name, state, undef)
            except ValueUnchanged: pass
            else: raise IllegalState('inconsistent attribute values')

    def checkAll(self, state):
        names = self.parts.copy()
        names.update(self.whole)
        names = names.keys()
        self.check(state, names, {})
    
    def sync(self, state, defs):
        undef = {}
        for name in defs:
            undef.update(self.getChildren(name))
            undef.update(self.getParents(name))
            undef.update(self.getSpouses(name))
        check_names = []
        for name in undef.keys():
            if name in defs:
                del undef[name]
                check_names.append(name)
        if check_names: # Hm...
            self.check(state, check_names, undef) # Hm...
        elif not undef: # Hm...
            self.checkAll(state) # Hm...
        stable = 0
        while undef and not stable:
            stable = 1
            for name in undef.keys():
                try:
                    newValue = self.newValue(name, state, undef)
                except (ValueUnchanged, CannotCalculate): pass
                else:
                    state[name] = newValue
                    del undef[name]
                    stable = 0
        return undef.keys()

    def newValue(self, name, state, undef):
        for parent in self.getParents(name).keys():
            if not undef.has_key(parent):
                pos = self.rules[parent].index(name)
                value = state[parent][pos]
                if equiv(state[name], value): raise ValueUnchanged
                return value
        value = []
        for child in self.getOrderedChildren(name):
            if undef.has_key(child):
                raise CannotCalculate
            else:
                value.append(state[child])
        value = tuple(value)
        if equiv(state[name], value): raise ValueUnchanged
        return value
