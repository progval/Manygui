from anygui import *
from anygui.backends.genericgui import OpenFileDialog
import sys

dir=''
if sys.platform in ['cygwin', 'linux1', 'linux2']:
    dir='/usr/lib'
else:
    dir='C:\\'

def openFileDlgCallback(event):
    print '>> file chosen -> ', event.file

app = Application(name='Test OpenFileDlg', version='1.0')
filedlg = OpenFileDialog(dir,'*')
link(filedlg, 'open', openFileDlgCallback)
app.add(filedlg)
app.run()
