from anygui import Window, Button, Label, application

w1 = Window(title='', size=(200,100))

lab = Label(text='Hello, world!', position=(30, 30))

w1.place(lab)

w2 = Window(title='This Window is visible', size=(200, 100))

b = Button(text='Show other window', position=(5, 5),
           size=(190, 90), action=w1.show)

w2.place(b)

w2.show()

application().run()
