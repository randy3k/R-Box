R package for Sublime Text
------------

**Important**: R-Box is now Sublime Text 3 only. The
[st2](https://github.com/randy3k/R-Box/tree/st2) branch contains the code for
Sublime Text 2. There is a huge change of R-Box in this Sublime Text 3 only
version
--- R-Box no longer ships with the "send text" functionality. R-Box will
mainly focus on the R language development. The "send text" functionality will
be exported to [SendText+](https://github.com/randy3k/SendTextPlus).

Features:

  - Autocompletions for [various packages](packages/).
  - Function hints in status bar for various packages.
  - Support Roxygen, Rcpp, R Sweave and R Markdown syntaxes. 
  - [knitr](https://github.com/yihui/knitr) build command for R markdown and Rnw files.
  - [R-Extended syntax](https://github.com/randy3k/R-Box/tree/master/syntax).

If you like it, you could send me some tips via [paypal](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=YAPVT8VB6RR9C&lc=US&item_name=tips&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted) or [gratipay](https://gratipay.com/~randy3k/).

![](https://raw.githubusercontent.com/randy3k/R-Box/screenshots/terminal.png)

### Getting start


- Install via [Package Control](https://sublime.wbond.net)


### Settings

See `Preference -> Package Settings -> R-Box`


### Autocompletions and status bar hints

Auto completions and status bar hints only support limited number of packages. R-Box will search for `library` or `require` statements in order to load the corresponding package support files. The support files are under the `packages` directory.  If your favorite packages are not listed there, you can generate the corresponding files by running `packages.R` in the following steps.

1. `Preference: Browse Packages` and create the directory `/Users/R-Box/` if it doesn't exist
2. Copy the file `packages.R` to `R-Box`
3. Run `Rscript packages.R <package name>`

This will create a json file under `packages` directory. 

#### SublimeLinter settings

To enable [SublimeLinter](http://www.sublimelinter.com/) via [SublimeLinter-contrib-R](https://github.com/jimhester/SublimeLinter-contrib-R) and  [lintr](https://github.com/jimhester/lintr), please add the following in the SublimeLinter user settings file:

```
    "syntax_map": {
        "r extended": "r"
    }
```

### License

R-Box is licensed under the MIT License. `AutoHotkeyU32.exe` under `bin` is included with its own license.
