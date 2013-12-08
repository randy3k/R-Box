Enhanced-R package for Sublime Text 2/3
------------
This package helps in writing R languages:

* More comprehensive Indentation and Syntax
* Send commands to different applications such as R GUI, Terminal and [SublimeREPL](https://github.com/wuub/SublimeREPL).
* Show function hint in status bar
 
<p align="center">
<img width=500 src="https://github.com/randy3k/Enhanced-R/raw/master/image/status.png">
</p>

----

Supported Applications
---------------
* R GUI on Windows and Mac
* Terminal and iTerm 2 on Mac
* Tmux and screen on Linux
* [SublimeREPL](https://github.com/wuub/SublimeREPL)
* (In beta) [RStudio](http://www.rstudio.com) on Mac

Note: For Windows, [AutoHotkey](http://www.autohotkey.com) which is an automation script is used
as a bridge between R and ST.

----

Key bindings
---------------
#### Sending Code (default: R)
**Keybinding:** `C-Enter`

* Send the selection to R (See settings for choosing default application)
* If no syntax is selected, it sends the whole line where the cursor stays at.
* Or if the current line ends with `{`, it finds the matching `}` and sends the whole block.

#### Changing Working Directory
**Keybinding:** `C-\`

* Change working directory to where the current working script is located

####  Sourcing file
**Keybinding:** `C-b`

* Tell R to source the working script

----

Settings
---------

Preferences -> Package Settings -> Enhanced R -> Settings

#### Application

* ``R Application Switch`` in Command Palette to switch between applications.

#### Application paths

* In default, Enhanced R will automatically search for applications. You may manually edit applications' paths.

#### Auto advance lines after sending command
```
{
    // auto advance lines after sending command
    "auto_advance": false,
}    
```
#### Packages for function hints.

```
{
    // a list of packages which functions will show in the status bar
    // "default_pkgs": ["base", "graphics", "grDevices", "methods", "stats", "utils"],
}
```

