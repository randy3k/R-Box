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
### Sending Code to R ###
**Keybinding:** `Cmd-enter`

* Send the selection to R
* If no syntax is selected, it sends the whole line where the cursor stays at.

### Changing Working Directory ###
**Keybinding:** `Cmd-\`

* Change working directory to where the current working script stays

### Sourcing file ###
**Keybinding:** `Cmd-.`

* Tell R to source the working script

