# TurtleGUI

A GUI for my
[turtle](https://github.com/Pitrified/go-turtle)
environment.

# IDEAs

### Misc

Use cards to keep elements grouped

### Structure

Image on the left, controls on a sidebar.

##### New world:

* size
* color picker

##### Turtle:

* rotate : -10 -1 -0.1 0.1 1 10
* entry+button rotate by that amount
* entry+button to set and show orientation

* move : -10 -1 -0.1 0.1 1 10
* entry+button move by that amount
* entries+button to set and show location
* Pos | x: entryX y: entryY btnSet

* color picker
* pen on
* pen off

##### Load commands:

* file selector
* something to show commands
* a pop-up window with some info on the command language syntax

##### Command history:

* just a list of old commands, not interactive (only scrollable)

##### Keyboard control:

* a whole lot of keyboard shortcut (SetOnTypedKey)

# TODOs

* Mic card, with credits and help popup.
* Splash window, with preference to not show again.
* Use fyne.canvas array to build the banks.
* Use custom scroller with preference to change the speed if needed.
