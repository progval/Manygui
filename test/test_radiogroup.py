from anygui import *
import sys

labels = ["Banana", "Chocolate", "Strawberry"]

grp = RadioGroup()
grp1 = RadioGroup()

def report(**kw):
    print grp.value
    print labels[grp.value], "selected (%d)" % grp.value

def report1(**kw):
    print grp1.value,type(grp1.value)
    print labels[grp1.value], "selected (%d)" % grp1.value
    
app = Application()

win = Window(width = 260, height = 150)
app.add(win)
for i in xrange(0, 3):
    btn = RadioButton(x = 30, y = (i+1) * 30, width = 100, height = 30, 
                      text = labels[i],
                      group = grp, value = i)
    link(btn, report)
    win.add(btn)

for i in xrange(0, 3):
    btn = RadioButton(x = 130, y = (i+1) * 30, width = 100, height = 30, 
                      text = 'x'+labels[i],
                      group = grp1, value = i)
    link(btn, report1)
    win.add(btn)

grp.value = 1
#grp1.value = 1

app.run()
