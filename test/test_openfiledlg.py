from anygui import *

app = Application(name='Test OpenFileDlg', version='1.0')
filedlg = AnyguiOpenFileDlg('/usr/lib','*')
app.add(filedlg)
app.run()
