from manygui.Components import Component
#from manygui.Exceptions import UnimplementedMethod
#from manygui.Models import ListModel
#from UserList import UserList
from manygui import Defaults,backendModule

#class ManyguiList(UserList):
#
#    def __init__(self,items=[]):
#        UserList.__init__(self,items)
#
#    def _set_value(self,items):
#        self.data = items

class ListBox(Component, Defaults.ListBox):

    def wrapperFactory(self):
        return backendModule().ListBoxWrapper(self)
