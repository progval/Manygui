"""
Test the Signals.py signal/handler logic.

Begin doctest cases:

>>> from anygui.Signals import *
>>> from test_signals import *
>>> s1 = Sender('s1')
>>> s2 = Sender('s2')
>>> r1 = Receiver('r1')
>>> r2 = Receiver('r2')
>>> r2.listenTo(s2)
>>> def allSigs(name):
...   print "Signal %s sent"%name
...
>>> connect(None,None,allSigs,{"signal_name":"name"})
>>> s1.sayHello("joe")
Saying hello to joe
Signal HELLO sent
>>> s2.sayHello("ani")
Saying hello to ani
r2: s2 said hello to ani
Signal HELLO sent
>>> s1.changeName("carl")
Sender s1 changing name to carl
r1: carl changed its name from s1 to carl
r2: carl changed its name from s1 to carl
Signal NAMECHANGE sent
>>> del r1
r1 DYING!!!
>>> s2.changeName("phil")
Sender s2 changing name to phil
r2: phil changed its name from s2 to phil
Signal NAMECHANGE sent
>>> disconnect(None,"NAMECHANGE",r2.handleNameChange)
>>> s1.changeName("bob")
Sender carl changing name to bob
Signal NAMECHANGE sent
>>> disconnect(None,None,allSigs)
>>> s1.changeName("fred")
Sender bob changing name to fred
>>> print "Hi"
Hi
"""

from anygui.Signals import *

class Sender:

    def __init__(self,name):
        self.name = name

    def sayHello(self,to):
        print "Saying hello to %s"%to
        signal(self,"HELLO",to=to)

    def changeName(self,name):
        print "Sender %s changing name to %s"%(self.name,name)
        oldname = self.name
        self.name = name
        signal(self,"NAMECHANGE",old=oldname,new=name)

class Receiver:

    def __init__(self,name):
        self.name = name
        # Register a handler for all name-change events.
        connect(None,"NAMECHANGE",self.handleNameChange,
                {"old":"oldname",
                 "new":"newname",
                 "signal_source":"src"
                 })

    def __del__(self):
        print "%s DYING!!!"%self.name

    def handleHello(self,signal_source,signal_name,to):
        print "%s: %s said hello to %s"%(self.name,signal_source.name,to)

    def handleNameChange(self,src,oldname,newname):
        print "%s: %s changed its name from %s to %s"%(self.name,src.name,
                                                       oldname,newname)

    def listenTo(self,sndr):
        connect(sndr,"HELLO",self.handleHello)


# Do the doctest thing.
if __name__ == "__main__":
    print "If you want detailed output, use \"python test_signals.py -v\"."
    print "No output after this line indicates success."
    import doctest, test_signals
    doctest.testmod(test_signals)
