from anygui import Application, Window, Menu, Label, link, TextField
from anygui.LayoutManagers import SimpleGridManager

app = Application()

win = Window(geometry=(50,50,100,100))
win.layout = SimpleGridManager(1,2)

# A menubar for the window.
mbar = Menu()
win.addMenu(mbar)

# A menu to choose skits.
skitMenu = Menu(text="Skit")
mbar.add(skitMenu)

# Populate the skit menu. The objects returned by the
# add...() calls are handles that permit us to operate
# on the menu items later.
dedPrt = skitMenu.addCommand(text="Dead Parrot")
pengTv = skitMenu.addCommand(text="Penguin on the Telly")
lumbrJk = skitMenu.addCommand(text="Lumberjack")

skitMenu.addSeparator()

# Enable or disable skit silliness: a checkable menu item.
enSilly = skitMenu.addCheck(text="Enable Silliness",on=0)
def enableSilly(ev):
    # Enable or disable the silliness selection based
    # on the value of the enSilly menu item.
    if enSilly.on:
        # subMenu is defined below.
        subMenu.enabled=1
    else:
        subMenu.enabled=0
link(enSilly,enableSilly)

# A sub-menu to allow silliness level to be selected:
# a mutually-exclusive set of checkable items (radio
# items?)
subMenu = Menu(text="Silliness...",enabled=0)
silliness = []
def handleSillySelect(ev):
    # Enforce mutual exclusion of silliness level.
    for item in silliness:
        if item != ev.source:
            item.on=0
        else:
            item.on = 1
for txt in ["Slight","Moderate","Unbearable"]:
    silliness.append(subMenu.addCheck(text=txt))
    link(silliness[-1],handleSillySelect)
skitMenu.add(subMenu)

skitMenu.addSeparator()
addCmd = skitMenu.addCommand(text="Add Skit")
def addSkit(*args,**kws):
    cmd = skitMenu.addCommand(text=entry.text,index=0)
    link(cmd,chooseSkit)
link(addCmd,addSkit)

# And a menu for help...
helpMenu = Menu(text="Help")
helpMenu.addCommand(text="About Anygui")
mbar.add(helpMenu)

lbl = Label(text="No skit selected")
win.add(lbl)
entry = TextField(text="Enter new skit",selection=(0,15))
win.add(entry)

def chooseSkit(ev):
    # Handle a skit choice. A menu event should have a
    # 'text' property containing the text of the menu item.
    lbl.text = ev.text

link(dedPrt,chooseSkit)
link(pengTv,chooseSkit)
link(lumbrJk,chooseSkit)

app.add(win)
app.run()
