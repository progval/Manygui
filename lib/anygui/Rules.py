
import re
name_pat = re.compile('[a-zA-Z_][a-zA-Z_0-9]*')

class NoChange(Exception): pass

class Rule:
    
    def __init__(self, ruleString):
        assert '"' not in ruleString and "'" not in ruleString
        name, expr = ruleString.split('=', 1)
        self.name = name.strip()
        self.expr = compile(expr.strip(), '', 'eval')
        self.deps = name_pat.findall(expr)

    def fire(self, scope):
        name = self.name
        value = eval(self.expr, scope)
        if value == scope[name]: raise NoChange
        scope[name] = eval(self.expr, scope)        

# TODO: - Add "rule checks" -- if a rule is satisfied, dependencies
#         are irrelevant.
#       - Fix iteration mechanism to make rule effects propagate
#         through several levels -- not just one
#       - Refactor adjust()
#       - Write separate test suite

class RuleEngine:
    """
    A simple rule engine which can maintain relationships between a
    set of key/value pairs in a dictionary.
    """
    
    def __init__(self):
        self.rules = {}
        self.is_dep = {}
        
    def addRule(self, ruleString):
        rule = Rule(ruleString)
        for dep in rule.deps: self.is_dep[dep] = 1
        self.rules.setdefault(rule.name, []).append(rule) # Ahem... ;)
        
    def adjust(self, vals, defs):
        undef = self.rules.copy() # Hm. Only need a set of the keys...
        dirty = 0
        for name in defs:
            if self.is_dep[name]: dirty = 1
            try: del undef[name]
            except: pass
        if not dirty: return
        for key in undef.keys():
            if not vals.has_key(key):
                del undef[key]
        stable = 0
        while undef and not stable:
            stable = 1
            for name in undef.keys():
                for rule in self.rules[name]:
                    for dep in rule.deps:
                        if undef.has_key(dep): break
                    else:               
                        try: rule.fire(vals)
                        except NoChange: pass
                        else: stable = 0
                        del undef[name]
                        break
        return undef.keys()

if __name__ == '__main__':
    eng = RuleEngine()
    # Hm. What is the "proper" rule set?
    eng.addRule('position = x, y')
    eng.addRule('x = position[0]')
    eng.addRule('y = position[1]')
    eng.addRule('size = width, height')
    eng.addRule('width = size[0]')
    eng.addRule('height = size[1]')
    eng.addRule('geometry = position + size')
    eng.addRule('geometry = x, y, width, height')
    eng.addRule('position = geometry[0], geometry[1]')
    eng.addRule('size = geometry[2], geometry[3]')

    vals = {}
    vals['x'] = 10
    vals['y'] = 20
    vals['width'] = 9999
    vals['height'] = 9999
    vals['size'] = 9999, 9999
    vals['position'] = 10, 10
    vals['geometry'] = 10, 10, 9999, 9999
    print eng.adjust(vals, ['y', 'x']) # 'x' shouldn't be necessary... Use value checks

    """
    print vals['position'], vals['geometry'] # Geometry isn't set properly here...
    vals['position'] = 42, 42
    print eng.adjust(vals, ['position'])
    print (vals['x'], vals['y']), vals['geometry']

    vals['geometry'] = 1, 2, 3, 4
    print eng.adjust(vals, ['geometry'])
    print (vals['x'], vals['y'], vals['width'], vals['height']), vals['position']+vals['size']
    """
