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

    def notify(self,target=None,change=None):
        print "View %d: value is %d"%(self.n,self.model.val)
        if change is not None:
            print "\tHints: %s"%str(change)

    def customNotify(self,target=None,change=None):
        print "View %d (custom callback): value is %d"%(self.n,self.model.val)
        if change is not None:
            print "\tHints: %s"%str(change)

m = Model()

v1 = View(m)
v2 = View(m)
v3 = View(m,"customNotify")

v1.notify()
v2.notify()
v3.notify()

m.setVal(3)

del v2

m.setVal(42)

m.setVal2(101)
m.setVal3(50,2)
m.notify_views()
m.notify_views()
