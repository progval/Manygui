'Anygui utilities.'

import sys
from Exceptions import InternalError

# for debugging...

def shortClassName(cl):
    name = cl.__name__
    lastdot = name.rfind('.')
    return name[lastdot+1:]

def objDescr(obj):
    return "%s@%s" % (shortClassName(obj.__class__),id(obj))

# --------------------------------------------------------------------

# To be phased out with the place() method
def flatten(seq):
    """
    Flatten a sequence. If seq is not a sequence, return [seq].  If
    seq is empty, return [].
    """
    try:
        if len(seq) > 0:
            seq[0]
    except:
        return [seq]
    result = []
    for item in seq:
        result += flatten(item)
    return result

# --------------------------------------------------------------------

def setterName(attribute):
    return 'set' + capitalizeAttribute(attribute)

def getterName(attribute):
    return 'get' + capitalizeAttribute(attribute)

def capitalizeAttribute(name):
    return name[0].upper() + name[1:]

def uncapitalizeAttribute(name):
    return name[0].lower() + name[1:]

def getSetter(obj, attr):
    return getattr(obj, setterName(attr), None)

def moreSpecific(name1, name2):
    s1 = name1.count('And')
    s2 = name2.count('And')
    return cmp(s1, s2)

def splitAccessorName(name):
    """
    Split accessor name by the word And, returning capitalised
    attribute names, as used internally by getSetters.
    """
    assert name[:3] in ['get', 'set']
    name = capitalizeAttribute(name[3:])
    result = []
    parts = name.split('And')
    for part in parts:
        if not part: continue
        if part[0].islower():
            if result and result[-1]:
                result[-1] = result[-1] + 'And' + part
            else:
                result.append('And' + part)
        else:
            result.append(part)
    return result

def getSetters(obj, attrs):
    """
    Get the most specific set of setter methods for a set of
    attributes.

    Given an object and a set of attribute names of the form fooBar
    and baBar this function will find setter methods in the object of
    the form setFooBar and setBaBar. If a more specific setter of the
    type setBaBarAndFooBar exists, that will be used instead.

    The return values are a list of the type [(setter, attrNames)] and
    a list of unhandled attributes.

    Since the word 'And' is used to split the attribute names, it
    cannot be used as a part of an attribute name as a separate
    word. (A string like 'Androgynous' is OK, though.)

    Example use:

    >>> class Test:
    ...     def setX(self, x): pass
    ...     def setY(self, y): pass
    ...     def setXAndY(self, x, y): pass
    ...     def setWidth(self, width): pass
    ...     def setHeight(self, height): pass
    ...     def setHeightAndWidth(self, height, width): pass
    ...     def setFooAndBar(self, foo, bar): pass # Not in alphabetic order
    ...     def setAndrogynous(self, a): pass
    ...     def setLikesAndy(self, la): pass
    ...
    >>> t = Test()
    >>> setters, unhandled = getSetters(t, ['x', 'y', 'width'])
    >>> len(setters), len(unhandled)
    (2, 0)
    >>> setters, unhandled = getSetters(t, ['x', 'width', 'height'])
    >>> len(setters), len(unhandled)
    (2, 0)
    >>> setters, unhandled = getSetters(t, ['likesAndy'])
    >>> len(setters), len(unhandled)
    (1, 0)
    >>> setters, unhandled = getSetters(t, ['androgynous'])
    >>> len(setters), len(unhandled)
    (1, 0)
    >>> setters, unhandled = getSetters(t, ['fooBar'])
    >>> len(setters), len(unhandled)
    (0, 1)
    >>> setters, unhandled = getSetters(t, ['bar', 'foo'])
    >>> len(setters), len(unhandled)
    (1, 0)
    """

    # TODO: Clean up and optimise(?)

    result = []
    attrs = attrs[:]
    attrs.sort()
    attrs = [capitalizeAttribute(name) for name in attrs]
    cands = [name for name in dir(obj) if name.startswith('set')]
    cands.sort(moreSpecific)
    cands.reverse()
    for cand in cands:
        setter = getattr(obj, cand)
        if not callable(setter): continue
        reqs = splitAccessorName(cand)
        for req in reqs:
            if not req in attrs: break
        else:
            for req in reqs: attrs.remove(req)
            reqs = [uncapitalizeAttribute(req) for req in reqs]
            reqs.sort()
            result.append((setter, reqs))
    return result, map(uncapitalizeAttribute, attrs)

def getGetter(obj, attr):
    return getattr(obj, getterName(attr), None)

# --------------------------------------------------------------------

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

class Options(Bunch): pass

import sys
class Log:

    def __init__(self,fileobj=None):
        if fileobj is None:
            fileobj = sys.stderr
        self._f = fileobj

    def log(self,*items):
        for i in items:
            self._f.write(str(i))
            self._f.write(' ')
        self._f.write('\n')

    def setLogFile(self,fileobj):
        if type(fileobj) == type(""):
            self._f = open(fileobj,"w")
        else:
            self._f = fileobj

    def flush(self):
        self._f.flush()

_logger = Log()

def log(*items):
  _logger.log(*items)

def setLogFile(fileobj):
    _logger.setLogFile(fileobj)

def logFlush():
    _logger.flush()

def logTraceback(n):
    import traceback
    traceback.print_exc(n,_logger._f)

_jython = sys.platform[:4] == 'java'

if _jython:
    import java
    generic_hash = java.lang.System.identityHashCode
    del java
else:
    generic_hash = id
    
class IdentityStack:
        def __init__(self):
            self._stk = []

        def pop(self):
            self._stk.pop()

        if _jython:
            def append(self,obj):
                self._stk.append(obj)
            def __contains__(self,obj):
                for cand in self._stk:
                    if cand is obj: return 1
                return 0
        else:
            def append(self,obj):
                self._stk.append(id(obj))
            def __contains__(self,obj):
                return id(obj) in self._stk

def topologicalSort(items, payload, constraints):
    """
    In-place topological sort (stable) of list 'items' to respect
    pairwise constraints coded as pairs (before, after) in sequence
    'constraints'. The 'payload' sequence will have its items subject
    to the same reordering as the 'items'.
    """
    # prepare mappings 'followers' [item -> set of items that must follow it]
    # and 'nleaders' [item -> number of items that must precede it]
    followers = {}
    nleaders = {}
    for before, after in constraints:
        if before in items and after in items:
            these_followers = followers.setdefault(before,{})
            if not these_followers.has_key(after):
                nleaders[after] = 1 + nleaders.get(after, 0)
                these_followers[after] = before
    # while there are items, pick one with no leaders, append it
    # to result, update list 'items' and mapping 'nleaders'
    result1 = []
    result2 = []
    while items:
        # find first item left that has no 'leaders'
        for i in xrange(len(items)):
            if nleaders.get(items[i], 0)==0: break
        else:
            raise InternalError(items, "dependency loop")
        # move the item from 'items' to 'result'
        item = items[i]
        piggyback = payload[i]
        del items[i], payload[i]
        result1.append(item)
        result2.append(piggyback)
        # update the mapping 'nleaders'
        for follower in followers.get(item,{}).keys():
            nleaders[follower] -= 1
    items[:] = result1
    payload[:] = result2

def _test():
    import doctest, Utils
    doctest.testmod(Utils)

if __name__ == '__main__': _test()
