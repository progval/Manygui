
class IllegalState(Exception): pass

# TODO:
# - Add checking of state integrity
# - Add support for "full sync" without defs

def addSubKey(dict, key, subkey):
    dict.setdefault(key, {})[subkey] = 1

# This is extremely klutzy and sketchy at the moment

class AggregateRuleEngine:
    
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
    
    def sync(self, state, defs):
        undef = {}
        for name in defs:
            undef.update(self.getChildren(name))
            undef.update(self.getParents(name))
            undef.update(self.getSpouses(name))
        stable = 0
        while undef and not stable:
            stable = 1
            for name in undef.keys():
                newValue = self.newValue(name, state, undef)
                if newValue is not None:
                    state[name] = newValue
                    del undef[name]
                    stable = 0
        return undef.keys()

    def newValue(self, name, state, undef):
        for parent in self.getParents(name).keys():
            if not undef.has_key(parent):
                pos = self.rules[parent].index(name)
                return state[parent][pos]
        value = []
        for child in self.getOrderedChildren(name):
            if undef.has_key(child):
                return None
            else:
                value.append(state[child])
        return tuple(value) or None
