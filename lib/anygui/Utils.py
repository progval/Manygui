'Anygui utilities.'

import sys

# To be phased out with the place() method
def flatten(seq):
    '''Flatten a sequence. If seq is not a sequence, return [seq].
    If seq is empty, return [].'''
    try:
        if len(seq) > 0:
            seq[0]
    except:
        return [seq]
    result = []
    for item in seq:
        result += flatten(item)
    return result


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

_logger = Log()

def log(*items):
  _logger.log(*items)

def setLogFile(fileobj):
    _logger.setLogFile(fileobj)
    
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
