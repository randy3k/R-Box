R package for Sublime Text
------------

**Important**: R-Box is now Sublime Text 3 only. The
[st2](https://github.com/randy3k/R-Box/tree/st2) branch contains the code for
Sublime Text 2. There is a huge change of R-Box in this Sublime Text 3 only
version --- 
R-Box no longer ships with the "send code" functionality. R-Box will
mainly focus on the R language development. The "send code" functionality is exported to [SendTextPlus](https://github.com/randy3k/SendTextPlus). You could choose the active program by the option `SendTextPlus: Choose Program` in command palette.

Features:

  - Autocompletions for [various packages](packages/).
  - Function hints in status bar for various packages.
  - Extend R Syntaxe
  - Support Roxygen, Rcpp, R Sweave and R Markdown syntaxes. 
  - Build commands for Rmarkdown and Rnw files.
  - A main menu inspired by [SublimeStudio](https://github.com/christophsax/SublimeStudio)

    <img src="https://raw.githubusercontent.com/randy3k/R-Box/screenshots/main_menu.png" width="200"/>

    

If you like it, you could send me some tips via [paypal](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=YAPVT8VB6RR9C&lc=US&item_name=tips&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted) or [gratipay](https://gratipay.com/~randy3k/).

### Getting start

- Install via [Package Control](https://sublime.wbond.net)


### Settings

See `Preference -> Package Settings -> R-Box`


### Autocompletions and status bar hints

Auto completions and status bar hints only support limited number of packages. R-Box will search for `library` or `require` statements in order to load the corresponding package support files. The support files are under the `packages` directory.  If your favorite packages are not listed there, you can generate the corresponding files by running `packages.R` in the following steps.

1. `Preference: Browse Packages` and create the directory `.../Users/R-Box/` if it doesn't exist
2. Copy the file `packages.R` to `R-Box`
3. Run `Rscript packages.R <package name>`

This will create a json file under `packages` directory. 

### License

R-Box is licensed under the MIT License.
