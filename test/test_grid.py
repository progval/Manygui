import manygui
app = manygui.Application()
win = manygui.Window()
frame=manygui.Frame(layout=manygui.LayoutManagers.GridManager(cols=2, rows=2))
for i in range(1, 10):
    frame.add(manygui.Button(text='Button %i' % i))
win.add(frame)
app.add(win)
app.run()
