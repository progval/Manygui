
# DEPRECATED

"""
Test the message handling callback adapter

>>> from test_callbacks import *
>>> c = ClickSimulator()
>>> c.simulate()
Mouse clicked at (1,2)
"""

from anygui.Messages import *

class ClickSimulator(CallbackAdapter):
    def click(self, x, y):
        print 'Mouse clicked at (%s,%s)' % (x, y)
    def simulate(self):
        send('click', self, x=1, y=2, time=1005497058.537949)

if __name__ == "__main__":
    print "If you want detailed output, use \"python test_callbacks.py -v\"."
    print "No output after this line indicates success."
    import doctest, test_callbacks
    doctest.testmod(test_callbacks)
