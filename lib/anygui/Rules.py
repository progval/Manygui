
import re
name_pat = re.compile('[a-zA-Z_][a-zA-Z_0-9]*')

class RuleEngine:
    """
    A simple rule engine which can maintain relationships between a
    set of key/value pairs in a dictionary.
    """
    
    def __init__(self):
        self.rules = {}
        self.deps = {}
        self.is_dep = {}
        
    def addRule(self, rule):
        assert '"' not in rule and "'" not in rule
        name, expr = rule.split('=', 1)
        name = name.strip()
        expr = expr.strip()
        deps = name_pat.findall(expr)
        for dep in deps: self.is_dep[dep] = 1
        self.deps[name] = deps
        self.rules[name] = compile(expr, '', 'eval')
        
    def adjust(self, vals, defs):
        undef = self.deps.copy()
        dirty = 0
        for name in defs:
            if self.is_dep[name]: dirty = 1
            try: del undef[name]
            except: pass
        if not dirty: return
        for key in undef.keys():
            if not vals.has_key(key):
                del undef[key]
        more = 1
        while undef and more:
            more = 0
            for name in undef.keys():
                for dep in self.deps[name]:
                    if undef.has_key(dep):
                        break
                else:
                    self.fire(name, vals)
                    del undef[name]
                    more = 1
        return undef.keys()
    
    def fire(self, name, scope):
        scope[name] = eval(self.rules[name], scope)

if __name__ == '__main__':
    eng = RuleEngine()
    eng.addRule('position = x, y')
    eng.addRule('x = position[0]')
    eng.addRule('y = position[1]')
    eng.addRule('size = width, height')
    eng.addRule('width = size[0]')
    eng.addRule('height = size[1]')
    eng.addRule('geometry = position + size')
    # How to add reverse here without overriding existent rule?
    # Must have multiple rules for each name... :I
    #eng.addRule('position = geometry[0], geometry[1]')
    #eng.addRule('size = geometry[2], geometry[3]')

    # TODO: Add "rule checks" -- if a rule is satisfied, dependencies
    # are irrelevant.

    vals = {}
    vals['x'] = 10
    vals['y'] = 20
    vals['position'] = 10, 10
    eng.adjust(vals, ['y', 'x']) # 'x' shouldn't be necessary... Use value checks
    print vals['position']
    vals['position'] = 42, 42
    eng.adjust(vals, ['position'])
    print (vals['x'], vals['y'])
