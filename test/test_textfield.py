from anygui import *
from anygui.Utils import log

def init_field(**kw):
    global tf, lbl
    tf.text = 'This is a TextField test.'
    tf.selection = (10,19)
    update_label()

def update_label(**kw):
    global tf, lbl
    sel = tf.selection
    text = tf.text
    lbl.text = text[:sel[0]] + \
               '[' + text[sel[0]:sel[1]] + ']' + \
                text[sel[1]:]

def print_contents(**kw):
    global tf
    log('Enter was pressed. Field contents:', tf.text)

tf = TextField(width=150, height=25)
link(tf, print_contents)
tf.text = ''
tf2 = TextField(width=150, height=25, editable=0)
tf2.text = 'Edit me... :P'
lbl = Label(width = 150, height=25, text = '')

update_btn = Button(width=50, height=30, text='Update')
link(update_btn, update_label)

reset_btn = Button(width=50, height=30, text='Reset')
link(reset_btn, init_field)

app = Application()

win = Window(title='TextField test', width=200, height=245)
app.add(win)

win.add([tf, tf2, lbl], left=25, right=25, top=40, hstretch=1,
          direction='down', space=20)

win.add([reset_btn, update_btn], right=25, bottom=25, vmove=1, hmove=1,
          direction='left', space=25)

init_field()
update_label()

app.run()
