import anygui
app = anygui.Application()
win = anygui.Window()
frame=anygui.Frame(layout=anygui.LayoutManagers.CircleManager())
for i in range(1, 10):
    frame.add(anygui.Button(text='Button %i' % i))
win.add(frame)
app.add(win)
app.run()
