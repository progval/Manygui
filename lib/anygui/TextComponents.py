from anygui.Components import Component
from anygui import Defaults, backendModule
from operator import add

class TextComponent(Component):

    pass

    #def __init__(self,*args,**kws):
    #    Component.__init__(self,*args,**kws)
    #    self.tags={}
    #
    #def addTag(self,tag,begin,end):
    #    try:
    #        self.tags[tag].append((begin,end))
    #    except KeyError:
    #        self.tags[tag] = [(begin,end)]
    #    self.push('tags')
    #
    #def removeTag(self,tag):
    #    self.tags[tag] = {}
    #    self.push('tags')
    #
    #def tagsAtPosition(self,pos):
    #    tdata = self.tags.items()
    #    def inRange((begin,end)): return pos>=begin and pos<end
    #    result = [tag for tag,ranges in tdata if reduce(add,map(inRange,ranges))]
    #    return result
