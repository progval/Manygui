from anygui import *
import sys

dir=''
if sys.platform in ['cygwin', 'linux1', 'linux2']:
    dir='/usr/lib'
else:
    dir='C:\\'

app = Application(name='Test OpenFileDlg', version='1.0')
filedlg = OpenFileDialog(dir,'*')
app.add(filedlg)
app.run()
