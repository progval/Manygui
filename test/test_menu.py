from anygui import Application, Window, Menu, MenuCheck, Label, link, TextField
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

# Populate the skit menu.
lbl = Label(text="No skit selected")
win.add(lbl)
def chooseSkit(ev):
    # Handle a skit choice. A menu event should have a
    # 'text' property containing the text of the menu item.
    lbl.text = ev.text

# The objects returned by the add...() calls are handles that permit
# us to operate on the menu items later.
dedPrt = skitMenu.addCommand(text="Dead Parrot")
pengTv = skitMenu.addCommand(text="Penguin on the Telly")
link(dedPrt,chooseSkit)
link(pengTv,chooseSkit)

# We can also supply a command to the command adder, which
# does an implicit link() for us. For menu structures
# that don't change much, this lets us build menus
# without having to deal with every menu item proxy.
# This works for checkboxes as well.
lumbrJk = skitMenu.addCommand(text="Lumberjack",command=chooseSkit)

skitMenu.addSeparator()

# Enable or disable skit silliness: a checkable menu item.
def enableSilly(ev):
    # Enable or disable the silliness selection based
    # on the value of the enSilly menu item.
    if enSilly.on:
        # subMenu is defined below.
        subMenu.enabled=1
    else:
        subMenu.enabled=0
enSilly = skitMenu.addCheck(text="Enable Silliness",on=0,command=enableSilly)

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

# We can set the contents of a menu in one go, if we want,
# instead of calling addThingy() a bunch of times.
for txt in ["Slight","Moderate","Unbearable"]:
    silliness.append(MenuCheck(text=txt,command=handleSillySelect))
subMenu.contents = silliness
skitMenu.add(subMenu)

skitMenu.addSeparator()
def addSkit(*args,**kws):
    cmd = skitMenu.addCommand(text=entry.text,index=0,command=chooseSkit)
addCmd = skitMenu.addCommand(text="Add Skit",command=addSkit)

# And a menu for help...
helpMenu = Menu(text="Help")
helpMenu.addCommand(text="About Anygui")
mbar.add(helpMenu)

entry = TextField(text="Enter new skit",selection=(0,15))
win.add(entry)

app.add(win)
app.run()
