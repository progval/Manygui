
# ********** Experimental version **********

# Doesn't work properly yet (the geometry test in test_rules fails.)
# E.g. position isn't directly damaged by geometry, and is therefore
# treated as defined (which it isn't)...

# TODO:
# Add error checking for underspecified stuff...
# Iterative stuff...?

class GroupRule:
    def __init__(self, name, parts):
        self.name = name
        self.deps = parts
        self.inverses = []
        for i in range(len(parts)):
            rule = SplitRule(parts[i], name, i)
            self.inverses.append(rule)
    def fire(self, state, locked):
        value = []
        for i in range(len(self.deps)):
            value.append(state[self.deps[i]])
        value = tuple(value)
        if self.name in locked and tuple(state[self.name]) != value:
            raise Exception # Be more specific... :)
        state[self.name] = value

class SplitRule:
    def __init__(self, name, whole, index):
        self.name = name
        self.deps = [whole]
        self.index = index
    def fire(self, state, locked):
        value = state[self.deps[0]][self.index]
        if self.name in locked and value != state[self.name]:
            raise Exception # Be more specific... :)
        state[self.name] = value
        if locked == ['geometry']: # DEBUG
            print self.name, '=', value, '[', self.deps[0], ']'

class RuleEngine:
    def __init__(self):
        self.rules = []
        self.damage = {}
    def getDamage(self, dep):
        return self.damage.setdefault(dep, {})
    def addDamage(self, dep, name):
        self.getDamage(dep)[name] = 1
    def define(self, string):
        name, expr = string.split('=')
        name = name.strip()
        deps = [n.strip() for n in expr.split(',')]
        rule = GroupRule(name, deps)
        self.rules.append(rule)
        self.rules.extend(rule.inverses)
        for rule in [rule] + rule.inverses:
            for dep in rule.deps:
                self.addDamage(dep, rule.name)
    def sync(self, state, locked):
        DEBUG = locked == ['geometry']
        undef = {}
        finished = {} # Hack
        for name in locked:
            undef.update(self.getDamage(name))
            finished[name] = 1
        stable = 0
        while undef and not stable:
            for rule in self.rules:
                if finished.has_key(rule.name) or not undef.has_key(rule.name): continue
                for dep in rule.deps:
                    if DEBUG: print dep
                    if undef.has_key(dep) and not finished.has_key(dep):
                        break
                else:
                    rule.fire(state, locked)
                    stable = 0
                    del undef[rule.name]
                    finished[rule.name] = 1
                    # Hack:
                    for key, val in self.getDamage(rule.name).items():
                        if not finished.has_key(key):
                            undef[key] = val
                    #undef.update(self.getDamage(rule.name))
        return undef.keys()
