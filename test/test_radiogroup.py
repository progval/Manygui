from anygui import Window, RadioButton, RadioGroup, application

labels = ["Banana", "Chocolate", "Strawberry"]

grp = RadioGroup()
grp1 = RadioGroup()

def report():
    print labels[grp.value], "selected (%d)" % grp.value

def report1():
    print labels[grp1.value], "selected (%d)" % grp1.value
    
win = Window(width = 260, height = 150)
for i in xrange(0, 3):
    btn = RadioButton(x = 30, y = (i+1) * 30, width = 100, height = 30, 
                      text = labels[i],
                      group = grp, value = i,
                      action = report)
    win.add(btn)

for i in xrange(0, 3):
    btn = RadioButton(x = 130, y = (i+1) * 30, width = 100, height = 30, 
                      text = 'x'+labels[i],
                      group = grp1, value = i,
                      action = report1)
    win.add(btn)

win.show()

application().run()
