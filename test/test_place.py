from manygui import *
from manygui.Utils import log
##from manygui import Window, View, CheckBox, Button, Label, \
##     RadioButton, RadioGroup, application
##from TestViews import TestView, BigTestView

# XXX for now only display Buttons
TestView = BigTestView = View = Button

#import pdb
#import sys

def pushed_it(event):
    log("Button pushed.")

def checked_it(event):
    log("Check boxes changed to:", cb1.on, cb2.on)

def option_chosen(event):
    log("Hoopy option %d chosen" % rg.value)

def main():
    global cb1, cb2, rg

    app = Application()

    win = Window(title = "Place Me By Your Side", width = 700, height = 500)
    app.add(win)

    view1 = TestView(width = 300, height = 200)
    
    view2 = BigTestView(width = 300, height = 300)

    cb1 = CheckBox(x = 10, y = 50,
                   width = 80, height = 20,
                   text = "Check Me!")
    link(cb1, checked_it)
    cb2 = CheckBox(x = 10, y = 70,
                   width = 110, height = 20,
                   text = "Check Me Too!")
    link(cb2, checked_it)

    rbs = []
    for i in range(1, 4):
      rbs.append(RadioButton(
        width = 150, height = 20,
        text = "Hoopy Option %d" % i,
        value = i))

    rg = RadioGroup(rbs)
    link(rg, option_chosen)

    pb = Button(x = 10, y = 10,
                width = 70, height = 30, 
                text = "Push Me!")
    link(pb, pushed_it)

    win.add(view1, position = (10, 10), border = 1)
    
    win.add((cb1, cb2), left = 10, top = (view1, 20))

    win.add(rbs, left = (view1, 20), top = 10, direction = 'down')

    win.add(pb, right = 20, bottom = 10, hmove = 1, vmove = 1)

    win.add([view2], 
              left = (rbs[0], 20), top = 10, 
              right = 20, bottom = (pb, 10),
              hstretch = 1, vstretch = 1)#, border = 1, hscroll = 1, vscroll = 1)

    label = Label(text = "Flavour:")
    #entry = TextField(width = 200, height = 28, text="Hi")
    entry = TextField(width = 200, height = 28)
    entry.text = "Hi"
    win.add(label, left = 10, top = (cb1, 20))
    win.add(entry, left = 10, top = (label, 10), border = 1)

    app.run()

#pdb.run("main()")

#try:
#  main()
#except:
#  sys.last_traceback = sys.exc_traceback
#  log(sys.exc_type, sys.exc_value)
#  pdb.pm()

main()
