"""
Doctest cases:

>>> m = Model()
>>> v1 = View(m)
>>> v2 = View(m)
>>> v3 = View(m,"customNotify")
>>> v1.model_changed()
View 1: value is 1
>>> v2.model_changed()
View 2: value is 1
>>> v3.model_changed()
View 3: value is 1
>>> m.setVal(3)
View 1: value is 3
Hints: []
View 2: value is 3
Hints: []
View 3 (custom callback): value is 3
Hints: []
>>> del v2
>>> m.setVal(42)
View 1: value is 42
Hints: []
View 3 (custom callback): value is 42
Hints: []
>>> m.setVal2(101)
>>> m.setVal3(50,2)
>>> m.notify_views()
View 1: value is 100
Hints: [('setVal2', (101,), {}), ('setVal3', (50, 2), {})]
View 3 (custom callback): value is 100
Hints: [('setVal2', (101,), {}), ('setVal3', (50, 2), {})]
>>> m.notify_views()
View 1: value is 100
Hints: []
View 3 (custom callback): value is 100
Hints: []
"""

from anygui.Mixins import Observable

class Model(Observable):

    def __init__(self):
        Observable.__init__(self)
        self.val = 1

    def setVal(self,nval):
        self.val = nval
        self.notify_views()

    def setVal2(self,nval):
        self.add_hint("setVal2",nval)
        self.val = nval

    def setVal3(self,nval1,nval2):
        self.add_hint("setVal3",nval1,nval2)
        self.val = nval = nval1 * nval2

class View:

    N = 1

    def __init__(self,model=None,callback=None):
        self.model = model
        model.add_view(self,callback)
        self.n = View.N
        View.N += 1

    def model_changed(self,target=None,change=None):
        print "View %d: value is %d"%(self.n,self.model.val)
        if change is not None:
            print "Hints: %s"%str(change)

    def customNotify(self,target=None,change=None):
        print "View %d (custom callback): value is %d"%(self.n,self.model.val)
        if change is not None:
            print "Hints: %s"%str(change)

# Do the doctest thing.
if __name__ == "__main__":
    import doctest, test_observable
    doctest.testmod(test_observable)
