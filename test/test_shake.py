from manygui import *
#from manygui.Utils import log

app = Application()

btn = Button(text='test!')
cbx = CheckBox()
lbl = Label()
lst = ListBox()
rdb = RadioButton()
txa = TextArea()
txf = TextField()

win = Window(title="Shake!",size=(120,380),position=(100,100))
app.add(win)
win.add((btn, cbx, lbl, lst, rdb, txa, txf),
          direction='down',
          left=10, top=10)

def get_geom(comp):
    return tuple(comp.geometry)

def set_geom(comp,g):
    comp.geometry = g

def get_single(comp):
    return comp.x,comp.y,comp.width,comp.height

def set_single(comp,g):
    comp.x = g[0]
    comp.y = g[1]
    comp.width = g[2]
    comp.height = g[3]

def get_possize(comp):
    return tuple(comp.position)+tuple(comp.size)

def set_possize(comp,g):
    comp.position = g[0],g[1]
    comp.size = g[2],g[3]

GET = { 'geom': get_geom, 'single': get_single, 'possize': get_possize }
SET = { 'geom': set_geom, 'single': set_single, 'possize': set_possize }

def shake_using(comp,aggr1,aggr2):
    fail = 0
    for set_aggr,delta in [(aggr1,+1),(aggr2,-1)]:
        g = GET[aggr1](comp)
        g = tuple([ v+delta for v in g ])
        SET[set_aggr](comp,g)
        g0 = GET[aggr1](comp)
        g1 = GET[aggr2](comp)
        if g0 != g or g1 != g:
            kind = comp.__class__.__name__
            print("!%s: %s<-%s => %s=%s %s=%s" % (kind,set_aggr,g,aggr1,g0,aggr2,g1))            
            fail += 1
    return fail

def shake_comp(comp):
    fail = 0
    K = list(GET.keys())
    for g in K:
        for s in K:
            fail += shake_using(comp,g,s)
    return fail

def shake(event):
    fail = 0
    for comp in [win,btn,cbx,lbl,lst,rdb,txa,txf]:
        fail += shake_comp(comp)
    if not fail:
        print("test passed")
    else:
        print('test failed',fail)


link(btn,shake)

app.run()
