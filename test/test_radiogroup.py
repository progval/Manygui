from manygui import *
from manygui.Utils import log

labels = ["Banana", "Chocolate", "Strawberry"]

grp = RadioGroup()
grp1 = RadioGroup()

def report(event):
    log(labels[grp.value], "selected (%d)" % grp.value)

def report1(event):
    log(labels[grp1.value], "selected (%d)" % grp1.value)
    
app = Application()

win = Window(width = 270, height = 150)
app.add(win)
box = GroupBox(x = 30, y = 30, width = 130, height = 90, text = 'Shakes')
win.add(box)
for i in range(0, 3):
    btn = RadioButton(x = 0, y = (i) * 30, width = 90, height = 30, 
                      text = labels[i],
                      group = grp, value = i)
    link(btn, Events.LeftClickEvent, report)
    box.add(btn)

for i in range(0, 3):
    btn = RadioButton(x = 170, y = (i+1) * 30, width = 100, height = 30, 
                      text = 'x'+labels[i],
                      group = grp1, value = i)
    link(btn, events.LeftClickEvent, report1)
    win.add(btn)

grp.value = 1

app.run()
