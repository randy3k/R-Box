Enhanced R: R Plugin for Sublime Text 2/3
=======================================

Introduction
------------
This plugin contains some simple features that helping writing R languages:
* More comprehensive Indentation and Syntax
* Useful commands
* Works on all Platforms

Useful Commands
---------------
### Sending Code to primary application (default: R)###
**Keybinding:** `Cmd-Enter`

* Send the selection to R
* If no syntax is selected, it sends the whole line where the cursor stays at.
* See settings to choose default R application to send to.

### Sending Code to secondary application (default: Terminal)###
**Keybinding:** `Cmd-Alt-Enter`

* Send the selection to R session in terminal
* An R session needs to be running on terminal.
* If no syntax is selected, it sends the whole line where the cursor stays at.
* Useful for people working on server

### Changing Working Directory (Primary)###
**Keybinding:** `Cmd-\`

* Change working directory to where the current working script stays

### Sourcing file (Primary)###
**Keybinding:** `Cmd-.`

* Tell R to source the working script

Kepmaps are changable by editing `Default (OSX).sublime-keymap`.

Settings
---------
### Rapp ###
**Default primary application:** `R`

**Default secondary application:** `Terminal`

* Type ``R Application Switcher`` in Command Palette to switch between `R`, `R64` and `Terminal`.