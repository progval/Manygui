from anygui import *

app = Application()

tf = TextField(text="Hello, world!")
tf.addTag("hi",0,5)
tf.addTag("ow",4,8)
tf.addTag("wo",7,12)

for pos in (0,4,5,7,8,10,12):
    print "Tags at position",pos,":",tf.tagsAtPosition(pos)
