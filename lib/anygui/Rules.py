
class IllegalState(Exception): pass

# TODO:
# - Add generic split/join mechanism etc.
# State checking:
# - If no def-names are given (full update), check that
#   there are no discrepancies between aggregates and their atomic
#   components
# - If def-names are given, for any discrepancies between atomic
#   components and aggregates, check that only either (1) the
#   aggregate is being redefined, or (2) one or more of the atomic
#   components of the aggregate (must include all the discrepant ones)
#   are being redefined

def addSubKey(dict, key, subkey):
    dict.setdefault(key, {})[subkey] = 1

class AggregateRuleEngine:
    
    def __init__(self):
        self.parts = {}
        self.whole = {}
        self.rules = {}

    def add(self, rule):
        """
        Add a rule to the rule engine.

        The rule must be a string of the form 'x = y, z, w' with a
        single name on the left hand side of the assignment, and a
        tuple (without parentheses) of names on the right hand side.
        """
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
            for whole in self.whole[name].keys():
                undef[whole] = 1
            for part in welf.parts[name].keys():
                undef[part] = 1

        # Add inconsistency checks here
        # (Possibly also below -- if an "illegal" computation causes
        # no change, there is no problem.)

        stable = 0
        while undef and not stable:
            stable = 1
            for name in undef.keys():
                # ...

        """
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
        """
