from anygui import *

class MyWindow(Window):
    pass

# For debugging purposes:
class CreationSentinel:
    'Calls win.ensure_created() when leaving local scope'
    def __init__(self, win):
        self.win = win
    def __del__(self):
        self.win.ensure_created()        

app = Application()

win = MyWindow(title="A Standard Window",
               width=220, height = 45)

def new_window():
    # This should not appear until the function returns:
    win = Window(title='Yay, another window!')

    sentinel = CreationSentinel(win)

    # Test for flashing (should not be visible):
    #for i in range(5):
    #    win.visible = not win.visible
    #win.visible = 1
    
    #print application()._windows

    # Debug:
    #del locals()['0']

btn = Button(text='Create new window', size=(200,25), x=10, y=10,
             action=new_window)
win.add(btn)

print application()._windows
print

#dlog = Window(title = "A Dialog Window", style = 'dialog',
#	      x = 100, y = 300, width = 300, height = 200)

#print application()._windows

app.run()

print application()._windows
