from anygui import *

app = Application()
win = Window(size=(280,200))
num = 3
opt = Options(y=10, width=80, height=25)
bns = [Button(opt, text='Frame %s' % i, x=(10+i*90)) for i in range(num)]
for btn in bns:
    win.add(btn)
opt = Options(geometry=(10,45,260,145), visible=0)
fms = [Frame(opt) for i in range(num)]
#fms = [Button(opt, text='Button %s' % i) for i in range(num)] # Debugging
for frm, i in zip(fms,range(num)):
    lbl = Label(text='This is Frame number %s.' % i)
    lbl.geometry = 10, 10, 200, 15
    frm.add(lbl) # Comment out for debugging
    win.add(frm)
callbacks = []
for i in range(num):
    def callback(i=i, **kw): # Store the index
        for j in range(num):
            if j!=i:
                fms[j].visible = 0
                print 'Frame %s hidden' % j
            else:
                fms[j].visible = 1
                print 'Frame %s shown' % j
    callbacks.append(callback)
for i in range(num):
    link(bns[i], 'action', callbacks[i])
app.run()
