from anygui import *
from anygui.Utils import log

the_text = """\
I like chinese,
I like chinese,
They only come up to your knees,
Yet they're always friendly and they're ready to please.

I like chinese,
I like chinese,
There's nine hundred million of them in the world today,
You'd better learn to love them, that's what I say.

I like chinese,
I like chinese,
They come from a long way overseas,
But they're cute, and they're cuddly, and they're ready to please.
"""

# FIXME: Change names -- text area used instead of label

def init_field(event=None):
    global ta, lbl
    ta.text = the_text
    ta.selection = (23,30)
    update_label()

def update_label(event=None):
    global ta, lbl
    sel = ta.selection
    text = ta.text
    print "############## selection = ", sel
    lbl.text = text[:sel[0]] + \
               '[' + text[sel[0]:sel[1]] + ']' + \
                text[sel[1]:]

app = Application()

ta = TextArea(width=150,height=100)
ta.text = ''
ta2 = TextArea(width=150,height=100, editable=0)
ta2.text = 'Edit me... :P'
lbl = TextArea(width=150, height=250, text='', editable=0)

update_btn = Button(width=50, height=30, text='Update')
link(update_btn, update_label)

reset_btn = Button(width=50, height=30, text='Reset')
link(reset_btn, init_field)

win = Window(title='TextArea test', width=400, height=670)
app.add(win)

win.add([ta, ta2, lbl], left=25, right=25, top=40, hstretch=1,
          direction='down', space=20)

win.add([reset_btn, update_btn], right=25, bottom=25, vmove=1, hmove=1,
          direction='left', space=25)

init_field()
update_label()

app.run()
