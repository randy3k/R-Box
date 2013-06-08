Enhanced R: R Plugin for Sublime Text 2/3
=======================================

Introduction
------------
This plugin contains some simple features that helping writing R languages:
* More comprehensive Indentation and Syntax
* Some useful key bindings
* Support multiple applications on Windows/Mac/Linux.
* For Windows, [AutoHotkey](http://www.autohotkey.com) which is an automation script is used 
and the binary exe is also included.

Some useful key bindings
---------------
#### Sending Code (default: R)
**Keybinding:** `Cmd-Enter`

* Send the selection to R (See settings for choosing default application)
* If no syntax is selected, it sends the whole line where the cursor stays at.

### Changing Working Directory
**Keybinding:** `Cmd-\`

* Change working directory to where the current working script stays

### Sourcing file (Primary)
**Keybinding:** `Cmd-b`

* Tell R to source the working script

Settings
---------
#### Application 

* Type ``R: Choose Application`` in Command Palette to switch between applications.
