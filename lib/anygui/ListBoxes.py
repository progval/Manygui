from anygui.Components import Component
#from anygui.Exceptions import UnimplementedMethod
#from anygui.Models import ListModel
#from UserList import UserList
from anygui import Defaults,backendModule

#class AnyguiList(UserList):
#
#    def __init__(self,items=[]):
#        UserList.__init__(self,items)
#
#    def _set_value(self,items):
#        self.data = items

class ListBox(Component, Defaults.ListBox):

    def wrapperFactory(self):
        return backendModule().ListBoxWrapper(self)
