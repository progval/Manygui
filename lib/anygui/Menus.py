from anygui.Exceptions import UnimplementedMethod
from anygui.Utils import flatten
from anygui.Proxies import Proxy
from anygui.Events import DefaultEventMixin
import anygui.Defaults as Defaults
from anygui import backendModule, link

# TODO: Use Container mixin?
#       Subclass Component?
#       Create MenuItem class...
#       Use contents instead of items?
#       Add items to defaults...


class MenuCommand(Proxy,DefaultEventMixin,Defaults.MenuCommand):
    def __init__(self, *args, **kw):
        DefaultEventMixin.__init__(self)
        Proxy.__init__(self, *args, **kw)
        if 'command' in kw.keys():
            link(self,kw['command'])

    def wrapperFactory(self):
        return backendModule().MenuCommandWrapper(self)

class MenuCheck(Proxy,DefaultEventMixin,Defaults.MenuCheck):
    def __init__(self, *args, **kw):
        DefaultEventMixin.__init__(self)
        Proxy.__init__(self, *args, **kw)
        if 'command' in kw.keys():
            link(self,kw['command'])

    def wrapperFactory(self):
        return backendModule().MenuCheckWrapper(self)

class MenuSeparator(Proxy,DefaultEventMixin,Defaults.MenuSeparator):
    def __init__(self, *args, **kw):
        DefaultEventMixin.__init__(self)
        Proxy.__init__(self, *args, **kw)

    def wrapperFactory(self):
        return backendModule().MenuSeparatorWrapper(self)

class Menu(Proxy, DefaultEventMixin, Defaults.Menu):
    
    def __init__(self, *args, **kwds):
        DefaultEventMixin.__init__(self)
        Proxy.__init__(self, *args, **kwds)
        self.contents = []

    def wrapperFactory(self):
        return backendModule().MenuWrapper(self)

    # Adders.
    def addCommand(self,text="COMMAND",enabled=1,index=None,command=None,*args,**kws):
        cmdItem = MenuCommand(text=text,*args,**kws)
        if command:
            link(cmdItem,command)
        self.add(cmdItem,index)
        return cmdItem

    def addCheck(self,text="CHECKBOX",enabled=1,index=None,command=None,*args,**kws):
        cmdItem = MenuCheck(text=text,*args,**kws)
        if command:
            link(cmdItem,command)
        self.add(cmdItem,index)
        return cmdItem

    def addSeparator(self,index=None):
        sepItem = MenuSeparator()
        self.add(sepItem,index)
        return sepItem

    def addMenu(self,text="MENU",enabled=1,index=None,*args,**kws):
        mnu = Menu(text=text,enabled=enabled,*args,**kws)
        self.add(mnu,index)
        return mnu

    def add(self,items,index=None):
        if index is None:
            index = len(self.contents)
        items = flatten(items)
        for item in items:
            self.contents.insert(index,item)
            index = index+1
            item.container = self
        self.push('contents')

    def remove(self, item):
        if item in self.contents:
            self.contents.remove(item)
            self.push()
