
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

class RuleEngine:
    """
    A simple rule engine which can maintain relationships between a
    set of key/value pairs in a dictionary.
    """
    
    def __init__(self):
        self.rules = {}
        self.affected = {}
        
    def addRule(self, ruleString):
        rule = Rule(ruleString)
        name = rule.name
        try: self.rules[name].append(rule)
        except KeyError: self.rules[name] = [rule]

    def setAffected(self, name, affected):
        self.affected[name] = affected
        
    def adjust(self, vals, defs):
        undef = {}
        for name in defs:
            for dep in self.affected[name]:
                if vals.has_key(dep):
                    if dep in defs: raise IllegalState
                    undef[dep] = 1
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
