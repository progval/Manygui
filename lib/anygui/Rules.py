
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
        value = eval(self.expr, globals(), scope)
        scope[name] = value

# FIXME: Full transitive closure doesn't make sense, since position
# depends on x and y depends on position etc... Is it necessary to
# have two different graphs, one for each "direction"?

class DependencyGraph:
    """
    Graph for representing rule dependencies.

    An edge A->B represents that the value of A must be known before B
    can be calculated.
    """
    def __init__(self):
        self.edges = {}
        self.nodes = {}
    def add(self, src, dst):
        # FIXME: Check that src != dst? "Self-dependency" doesn't make sense...
        self.nodes[src] = 1
        self.nodes[dst] = 1
        self.edges.setdefault(src,{})[dst] = 1
        self.dirty = 1
    def __contains__(self, (src, dst)):
        if self.dirty: self.transitiveClosure()
        if not self.edges.has_key(src): return 0
        return self.edges[src].has_key(dst)
    def children(self, node):
        if self.dirty: self.transitiveClosure()
        try: return self.edges[node].keys()
        except KeyError: return []
    def transitiveClosure(self):
        self.dirty = 0
        closure = {}
        nodes = self.nodes.keys()
        for x in nodes:
            for y in nodes:
                if x==y or (x, y) in self:
                    closure[x, y] = 1
        for k in nodes:
            for x in nodes:
                for y in nodes:
                    if closure.has_key((x, y)): continue
                    if closure.has_key((x, k)) and \
                       closure.has_key((k, y)):
                        closure[x, y] = 1

        for x, y in closure.keys():
            if x != y: self.add(x, y)

class RuleEngine:
    """
    A simple rule engine which can maintain relationships between a
    set of key/value pairs in a dictionary.
    """
    
    def __init__(self):
        self.rules = {}
        self.deps = DependencyGraph()
        self.dirty = 0
        
    def addRule(self, ruleString):
        rule = Rule(ruleString)
        name = rule.name
        try: self.rules[name].append(rule)
        except KeyError: self.rules[name] = [rule]
        for dep in rule.deps:
            self.deps.add(dep, name)
        
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
