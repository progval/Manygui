from anygui import *

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
They come from a long way oversease,
But they're cute, and they're cuddly, and they're ready to please.
"""

def init_field():
    global ta, lbl
    ta.model.value = the_text
    ta.selection = (23,30)
    update_label()

def update_label():
    global ta, lbl
    sel = ta.selection
    text = ta.model.value
    lbl.text = text[:sel[0]] + \
               '[' + text[sel[0]:sel[1]] + ']' + \
                text[sel[1]:]

ta = TextArea(size=(150,100))
ta.model.value = ''
ta2 = TextArea(size=ta.size, editable=0)
ta2.model.value = 'Edit me... :P'
lbl = Label(width=150, height=250, text='')

update_btn = Button(width=50, height=30, text='Update', action=update_label)
reset_btn = Button(width=50, height=30, text='Reset', action=init_field)

app = Application()

win = Window(title='TextArea test', width=400, height=670)

win.place([ta, ta2, lbl], left=25, right=25, top=40, hstretch=1,
          direction='down', space=20)

win.place([reset_btn, update_btn], right=25, bottom=25, vmove=1, hmove=1,
          direction='left', space=25)

init_field()
update_label()

win.show()

app.run()
