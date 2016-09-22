R package for Sublime Text
------------

<a href="https://packagecontrol.io/packages/R-Box"><img src="https://packagecontrol.herokuapp.com/downloads/R-Box.svg"></a>
<a href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&amp;business=Randy%2ecs%2elai%40gmail%2ecom&amp;lc=US&amp;item_name=Package&amp;currency_code=USD&amp;bn=PP%2dDonationsBF%3apaypal%2ddonate%2dyellow%2esvg%3aNonHosted" title="Donate to this project using Paypal"><img src="https://img.shields.io/badge/paypal-donate-blue.svg" /></a>
<a href="https://gratipay.com/~randy3k/" title="Donate to this project using Gratipay"><img src="https://img.shields.io/badge/gratipay-donate-yellow.svg" /></a>

Features:

- Autocompletions for [various packages](packages/).
- Popup function hints.
- Extend R Syntax
- Support Roxygen, Rcpp, R Sweave and R Markdown syntaxes. 
- Build commands for Rmarkdown and Rnw files.
- R-Box main menu (if [SendREPL](https://github.com/randy3k/SendREPL) is installed)

<img src="https://raw.githubusercontent.com/randy3k/R-Box/screenshots/main_menu.png" width="200"/>


### Installation

- Install via [Package Control](https://sublime.wbond.net)

### Settings

See `Preference -> Package Settings -> R-Box`


### Send Code to Terminal / R GUI / RStudio
R-Box no longer ships with the "send code" functionality. The functionality is
exported to [SendREPL](https://github.com/randy3k/SendREPL). You could choose
the active program by the option `SendREPL: Choose REPL Program` in command
palette. For histroical reasons, if you are still using
[SendTextPlus](https://github.com/randy3k/SendTextPlus), the corresponding
command is `SendTextPlus: Choose Program`.
