
import re
name_pat = re.compile('[a-zA-Z_][a-zA-Z_0-9]*')

class IllegalState(Exception): pass

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
        scope[name] = eval(self.expr, scope)        

class DependencyGraph:
    """
    Graph for representing rule dependencies.

    An edge A->B represents that the value of A must be known before B
    can be calculated.
    """
    def __init__(self):
        self.edges = {}
    def addEdge(self, src, dst):
        self.edges.setdefault(src,{})[dst] = 1
    def children(self, node):
        try: return self.edges[node].keys()
        except KeyError: return []
    def closure(self, node):
        for dep in self.dependents(node):
            self.addEdge(node, dep)
    def dependents(self, node, status=None):
        if status is None: status = {}
        status[node] = 1
        result = []
        for child in self.children(node):
            if not status.has_key(child):
                result.extend(self.dependents(child, status))
        status[node] = 'finished'
        return result

class RuleEngine:
    """
    A simple rule engine which can maintain relationships between a
    set of key/value pairs in a dictionary.
    """
    
    def __init__(self):
        self.rules = {}
        self.deps = DependencyGraph()
        
    def addRule(self, ruleString):
        rule = Rule(ruleString)
        name = rule.name
        try: self.rules[name].append(rule)
        except KeyError: self.rules[name] = [rule]
        for dep in rule.deps:
            self.deps.addEdge(dep, name)
            self.deps.closure(dep)
        
    def adjust(self, vals, defs):
        undef = {}
        for name in defs:
            for child in self.deps.children(name):
                if vals.has_key(child):
                    if child in defs: raise IllegalState
                    undef[child] = 1
        stable = 0
        while undef and not stable:
            stable = 1
            for name in undef.keys():
                for rule in self.rules[name]:
                    for dep in rule.deps:
                        if undef.has_key(dep): break
                    else:               
                        rule.fire(vals)
                        stable = 0
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

    print eng.adjust(vals, ['y'])

    print vals['position'], vals['geometry']
    vals['position'] = 42, 42
    print eng.adjust(vals, ['position'])
    print (vals['x'], vals['y']), vals['geometry']

    vals['geometry'] = 1, 2, 3, 4
    print eng.adjust(vals, ['geometry'])
    print (vals['x'], vals['y'], vals['width'], vals['height']), vals['position']+vals['size']

    # If the "illegal state" actually checked the expression and the
    # values etc. (no change), this shouldn't raise an exception...
    try: eng.adjust(vals, ['x', 'position'])
    except IllegalState: print 'Expected exception received'
