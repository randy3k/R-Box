R Plugin for Sublime Text 2
====================

Introduction
------------
This plugin contains some simple features that helping writing R languages:
* Indentation corrections
* Useful commands

Indentation corrections
-----------------------
It corrects the strange behavior when `for`, `while`, `if`, `else` and `repeat` are used without braces. In this situation, original indentation rule does not indent the next line. e.g.:

    for (i in (1:10))
    cat('Hello, baby!')

The correct indentation rule now indents like

    for (i in (1:10))
        cat('Hello, baby!')

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
**Default primary application:** `R64`

**Default secondary application:** `Terminal`

* Type ``Rapp Switcher`` in Command Palette to switch between `R`, `R64` and `Terminal`.<br>
* Or edit Rsublime.sublime-settings to change settings