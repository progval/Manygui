
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
    def dependents(self, node, visited=None):
        if visited is None: visited = {}
        visited[node] = 1
        result = []
        for child in self.children(node):
            if not visited.has_key(child):
                result.extend(self.dependents(child, visited))
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
