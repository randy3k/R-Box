R package for Sublime Text
------------

Features:

  1. Multi platform support (windows/mac/linux)
  2. Send commands to various applicaionts (R gui, Terminal, iTerm 2, screen, tmux...)
  3. Function hints in status bar
  4. Autocompletions for base R commands
  5. Support Roxygen, Rcpp, R Sweave and R Markdown syntaxes. 
  6. [knitr](https://github.com/yihui/knitr) build command for R markdown and Rnw files.

This package contains an extended version of the R syntax
definition, so you can safely disable the default `R` package.
If you are only interested in the syntax files, check [R-Extended](https://github.com/randy3k/R-Extended).

If you like it, you could send me some tips via [![](http://img.shields.io/gittip/randy3k.svg)](https://www.gittip.com/randy3k).

![](https://raw.githubusercontent.com/randy3k/R-Box/master/screenshots/terminal.png)

### Getting start


- Install via [Package Control](https://sublime.wbond.net)



### Usage

In the following, `C` is `ctrl` for Windows/Linux, `cmd` for Mac.

- `C + enter` to send code to gui/terminal. R.app is the default for mac, R64.exe is default for windows and tmux is the default for linux. To change the application, do `C + shift + p` -> `R-Box Application`.
- `C + \` to change working dir
- `C + b` to source the current R file, or to run [knitr](https://github.com/yihui/knitr) for Rnw or R markdown files.


### Settings

See `Preference -> Package Settings -> R-Box`


### License

R-Box is licensed under the MIT License. Files under `bin` are included with their own licenses.
