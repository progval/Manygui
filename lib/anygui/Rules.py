
class IllegalState(Exception): pass
class CannotCalculate(Exception): pass
class ValueUnchanged(Exception): pass

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
            try: self.newValue(name, state, undef)
            except ValueUnchanged: pass
            except CannotCalculate: pass # Hm...
            else: raise IllegalState('inconsistent attribute values')

    def checkAll(self, state):
        names = self.parts.copy()
        names.update(self.whole)
        names = names.keys()
        self.check(state, names, {})
    
    def sync(self, state, defs):
        """
        Sync a state dictionary according to the defined rules.

        This method works as follows:

          1. For each defined name, add all dependents to the set of
             undefined names.

          2. If any of the defined names are also in the set of
             undefined names, remove them from the set of undefined
             names and schedule them for checking.

          3. For each name scheduled for checking, check that it will
             not receive a new value from the newValue method.

          4. ... [FIXME]
          
        """
        # Probably not quite correct yet
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
        """
        Calculates a new value for a given name.

        This method may do one of three things:

        1. Return a new value

        If a rule is found that defines the given name and that
        doesn't have any undefined dependencies, the new value is
        calculated. If it is different from the previous value, it is
        returned.

        2. Raise ValueUnchanged

        If a value is calculated as per alternative 1 but it is
        equivalent (as defined by the equiv function) to the current
        value, ValueUnchanged is raised.

        3. Raise CannotCalculate

        If no rule is found that defines the given name and that
        doesn't have any undefined dependencies, CannotCalculate is
        raised.
        """
        for parent in self.getParents(name).keys():
            if not undef.has_key(parent):
                pos = self.rules[parent].index(name)
                value = state[parent][pos]
                break
        else:
            value = []
            for child in self.getOrderedChildren(name):
                if undef.has_key(child):
                    raise CannotCalculate
                else:
                    value.append(state[child])
            value = tuple(value)
        if equiv(state[name], value): raise ValueUnchanged
        return value
