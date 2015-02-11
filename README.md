R package for Sublime Text
------------

Features:

  1. Multi platform support (windows/mac/linux)
  2. Send commands to various applicaionts. 
    - Mac: R gui, Terminal, iTerm 2; 
    - Unix: screen, tmux; 
    - Windows: R gui, Cygwin, [Cmder](http://bliker.github.io/cmder/) (see below); 
    - SublimeREPL
  3. Function hints in status bar
  4. Autocompletions for base R commands
  5. Support Roxygen, Rcpp, R Sweave and R Markdown syntaxes. 
  6. [knitr](https://github.com/yihui/knitr) build command for R markdown and Rnw files.

If you are only interested in the syntax files, checkout [R-Extended](https://github.com/randy3k/R-Extended).

If you like it, you could send me some tips via [![](http://img.shields.io/gittip/randy3k.svg)](https://www.gittip.com/randy3k).

![](https://raw.githubusercontent.com/randy3k/R-Box/screenshots/terminal.png)

### Getting start


- Install via [Package Control](https://sublime.wbond.net)



### Usage

In the following, `C` is `ctrl` for Windows/Linux, `cmd` for Mac.

- `C + enter` to send code to gui/terminal. R.app is the default for mac, R64.exe is default for windows and tmux is the default for linux. To change the application, do `C + shift + p` -> `R-Box Application`.
- `C + \` to change working dir
- `C + b` to source the current R file, or to run [knitr](https://github.com/yihui/knitr) for Rnw or R markdown files.


### Settings

See `Preference -> Package Settings -> R-Box`

### FAQ

#### SublimeLinter settings

To enable [SublimeLinter](http://www.sublimelinter.com/) via [SublimeLinter-contrib-R](https://github.com/jimhester/SublimeLinter-contrib-R) and  [lintr](https://github.com/jimhester/lintr), please add the following in the SublimeLinter user settings file:

```
    "syntax_map": {
        "r extended": "r"
    }
```

#### Cmder settings

1. Due to this [bug!?](http://www.autohotkey.com/board/topic/92360-controlsend-messes-up-modifiers/), you have to change the paste shortcut of Cmder from `shift+insert` to `ctrl+shift+v` in Cmder settings.

2. Go to `Paste` in the settings, uncheck, "Confirm <enter> keypress" and "Confirm pasting more than..."


### License

R-Box is licensed under the MIT License. Files under `bin` are included with their own licenses.
