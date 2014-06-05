R package for Sublime Text 3
------------

It is a next generation of [Enhanced-R](https://github.com/randy3k/Enhanced-R). I have refactored the
original code and the old settings are not compatible with the current setup,
so I opened a new repo for it.

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

### Getting start


- Install via [Package Control](https://sublime.wbond.net)



### Usage

`C` is `ctrl` for Windows/Linux, `cmd` for Mac.

Send Command to GUI/Terminal.

- `C + enter` to send code to gui/terminal
- `C + \` to change working dir
- `C + b` to source the current R file, or to run [knitr](https://github.com/yihui/knitr) for Rnw or R markdown files.

Change R Applications

- `C + shift + p` -> `R-Box Application`


### Settings

See `Preference -> Package Settings -> R-Box`


### License

R-Box is licensed under the MIT License. Files under `bin` are included with their own licenses.
