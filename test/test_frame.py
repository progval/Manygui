from anygui import *

app = Application()
win = Window(size=(280,200))
app.add(win)
num = 3
opt = Options(y=10, width=80, height=25)
bns = [Button(opt, text='Frame %s' % i, x=(10+i*90)) for i in range(num)]
for btn in bns:
    win.add(btn)
opt = Options(geometry=(10,45,260,145), visible=0)
fms = [Frame(opt) for i in range(num)]
#fms = [Button(opt, text='Button %s' % i) for i in range(num)] # Debugging
n = 0
for frm, i in zip(fms,range(num)):
    lbl = Label(text='This is Frame number %s.' % i)
    lbl.geometry = 10, 10, 200, 15
    btn = Button(text = 'A button')

    frm1 = Frame()
    frm1.geometry = (20,20,150,40)
    lbl1 = Label(text="Subframe %d"%n)
    n += 1
    lbl1.geometry = 10, 10, 100, 30
    btn1 = Button(text="A button %d"%n,geometry=(20,20,100,40))
    frm1.add(lbl1,top=10,left=10)
    frm1.add(btn1,top=lbl1,left=10)

    frm2 = Frame()
    frm2.geometry = (20,20,150,40)
    lbl2 = Label(text="Subframe %d"%n)
    n += 1
    lbl2.geometry = 10, 10, 100, 30
    btn2 = Button(text="A button %d"%n,geometry=(20,20,100,40))
    frm2.add(lbl2,top=10,right=10)
    frm2.add(btn2,top=lbl1,left=10)

    frm.add(lbl,right=10,top=10,hmove=1) # Comment out for debugging
    frm.add(btn,right=50,top=lbl,hstretch=1)
    frm.add(frm1,left=10,bottom=30,top=btn,vstretch=1)
    frm.add(frm2,right=10,bottom=55,top=btn,hmove=1,vstretch=1)
    win.add(frm,top=60,left=10,right=10,bottom=10,hstretch=1,vstretch=1)
callbacks = []
for i in range(num):
    def callback(i=i,*args,**kws): # Store the index
        for j in range(num):
            if j!=i:
                fms[j].visible = 0
                print 'Frame %s hidden' % j
            else:
                fms[j].visible = 1
                print 'Frame %s shown' % j
    callbacks.append(callback)
for i in range(num):
    link(bns[i], callbacks[i])
app.run()
