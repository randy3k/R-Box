R package for Sublime Text
------------

Features:

  - Send commands to various programs. 
    - Mac: R gui, Terminal, iTerm 2; 
    - Unix: screen, tmux; 
    - Windows: R gui, Cygwin, [Cmder](http://bliker.github.io/cmder/) (see below to configure Cmder); 
    - SublimeREPL
  - Autocompletions for various packages.
  - Function hints in status bar for various packages.
  - Support Roxygen, Rcpp, R Sweave and R Markdown syntaxes. 
  - [knitr](https://github.com/yihui/knitr) build command for R markdown and Rnw files.

If you are only interested in the syntax files, checkout [R-Extended](https://github.com/randy3k/R-Extended).

If you like it, you could send me some tips via [paypal](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=YAPVT8VB6RR9C&lc=US&item_name=tips&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted) or [gratipay](https://gratipay.com/~randy3k/).

![](https://raw.githubusercontent.com/randy3k/R-Box/screenshots/terminal.png)

### Getting start


- Install via [Package Control](https://sublime.wbond.net)



### Usage

In the following, <kbd>C</kbd> is <kbd>ctrl</kbd> for Windows/Linux, <kbd>cmd</kbd> for Mac.

- <kbd>C</kbd> + <kbd>enter</kbd> to send code to gui/terminal. R.app is the default for mac, R64.exe is default for windows and tmux is the default for linux. To change the application, do <kbd>C</kbd> + <kbd>shift</kbd> + <kbd>p</kbd> -> `R-Box: Choose Program`.
- <kbd>C</kbd> + <kbd>\\</kbd> to change working dir
- <kbd>C</kbd> + <kbd>b</kbd> to source the current R file, or to run [knitr](https://github.com/yihui/knitr) for Rnw or R markdown files.


### Settings

See `Preference -> Package Settings -> R-Box`


### Autocompletions and status bar hints

Auto completions and status bar hints only support limited number of packages. R-Box will search for `library` or `require` statements in order to load the corresponding package support files. The support files are under the `packages` directory.  If your favorite packages are not listed there, you can generate the corresponding files by running `packages.R` in the following steps.

1. `Preference: Browse Packages` and create the directory `.../Packages/Users/R-Box/` if it doesn't exist
2. Copy the file `packages.R` to `R-Box`
3. Run `Rscript packages.R <package name>`

This will create a json file under `packages` directory. You could also submit a pull request for the package support files.

### Customize syntax highlight packages

In default, only functions from the default libraries are highlighted. To add syntax highlight for different packages, do the followings.

1. `Preference: Browse Packages` and create the directory `.../Packages/Users/R-Box/` if it doesn't exist
2. Copy the file `syntax.R` to `R-Box`
3. Edit the `packages` variables in `syntax.R`
4. Run `Rscript syntax.R`

This will create a syntax file `R Functions.tmlanguage` under `syntax` directory.  Sublime will load the file automatically.

### FAQ

#### SublimeLinter settings

To enable [SublimeLinter](http://www.sublimelinter.com/) via [SublimeLinter-contrib-R](https://github.com/jimhester/SublimeLinter-contrib-R) and  [lintr](https://github.com/jimhester/lintr), please add the following in the SublimeLinter user settings file:

```
    "syntax_map": {
        "r extended": "r"
    }
```

#### Cmder settings

There are two things that you need to do:

1. Due to this [bug!?](http://www.autohotkey.com/board/topic/92360-controlsend-messes-up-modifiers/), you have to change the paste shortcut of Cmder from <kbd>shift</kbd>+<kbd>insert</kbd> to <kbd>ctrl</kbd>+<kbd>shift</kbd>+<kbd>v</kbd> in Cmder settings.

2. Go to `Paste` in the settings, uncheck, "Confirm <enter> keypress" and "Confirm pasting more than..."


### License

R-Box is licensed under the MIT License. `AutoHotkeyU32.exe` under `bin` is included with its own license.
