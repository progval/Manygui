from anygui import backend
import anygui

print 'The current backend is:', backend()
print "No output below this line indicates success"
assert backend() in anygui._backends
