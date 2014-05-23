R-Box package for Sublime Text 3
------------

It is a next generation of the R package
[Enhanced-R](https://github.com/randy3k/Enhanced-R). I have refactored the
original code and the old settings are not compatible with the current setup,
so I decided to create a new repo for it.

This package contains a extended version of the R syntax
definition, so you do not have to install
any syntax definitions for R (and savely disable the default `R` package). 

Features:

  1. Multi platform support (windows/mac/linux)
  2. Send commands to various applicaionts (R gui, Terminal, iTerm 2, screen, tmux...)
  3. Function hints in status bar
  4. Autocompletions for base R commands
  5. Support Roxygen, Rcpp, R Sweave and R Markdown syntaxes. 

### Getting start


- Install via [Package Control](https://sublime.wbond.net)



### Usage

`C` is `ctrl` for Windows/Linux, `cmd` for Mac.

Send Command to GUI/Terminal.

- `C + enter` to send code to gui/terminal
- `C + \` to change working dir
- `C + b` to source the current file
 
Change R Applications

- `C + shift + p` -> `R-Box Application`


### Settings

See `Preference -> Package Settings -> R-Box`
