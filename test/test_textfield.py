from anygui import Window, TextField, Button, Label, Application

def init_field():
    global tf, lbl
    tf.model.value = 'This is a TextField test.'
    tf.selection = (10,19)
    update_label()

def update_label():
    global tf, lbl
    sel = tf.selection
    text = tf.model.value
    lbl.text = text[:sel[0]] + \
               '[' + text[sel[0]:sel[1]] + ']' + \
                text[sel[1]:]

def print_contents():
    global tf
    print 'Enter was pressed. Field contents:', tf.model.value

tf = TextField(width=150, height=25, action=print_contents)
tf.model.value = ''
tf2 = TextField(width=150, height=25, editable=0)
tf2.model.value = 'Edit me... :P'
lbl = Label(width = 150, height=25, text = '')

update_btn = Button(width=50, height=30, text='Update', action=update_label)
reset_btn = Button(width=50, height=30, text='Reset', action=init_field)

app = Application()

win = Window(title='TextField test', width=200, height=245)

win.place([tf, tf2, lbl], left=25, right=25, top=40, hstretch=1,
          direction='down', space=20)

win.place([reset_btn, update_btn], right=25, bottom=25, vmove=1, hmove=1,
          direction='left', space=25)

init_field()
update_label()

win.show()

app.run()
