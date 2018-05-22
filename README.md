R package for Sublime Text
------------

<a href="https://packagecontrol.io/packages/R-Box"><img src="https://packagecontrol.herokuapp.com/downloads/R-Box.svg"></a>
<a href="https://www.paypal.me/randy3k/5usd" title="Donate to this project using Paypal"><img src="https://img.shields.io/badge/paypal-donate-blue.svg" /></a>


Improve your R coding experiences with Sublime Text!

**News**

- The R Extended Syntax has been merged to Sublime Text. R-Box is no longer shipping a copy of it. Use the syntax `R` comes with Sublime Text.

- I am working on the next iteration of R-Box - `R-IDE` at https://github.com/REditorSupport/sublime-ide-r. R-IDE depends on the [language server protocol](https://github.com/tomv564/LSP) and is now only recomended for advanced users.


## Features highlight!

<table>
    <tr>
        <th>Auto Completions</th>
        <th>R-Box Main Menu</th>
    </tr>
    <tr>
        <td width="50%">
            <img src="https://cloud.githubusercontent.com/assets/1690993/20997623/44433e6a-bcd5-11e6-9cac-44ea07c961d9.png" width="100%">
        </td>
        <td width="50%">
            <img src="https://user-images.githubusercontent.com/1690993/29596130-ae7efb5a-8789-11e7-9d73-0714b62b6ebb.png" width="100%">
        </td>
    </tr>
    <tr>
        <td width="50%">Installed packages; Objects in packages; Function arguments.</td>
        <td width="50%">Some features are provided by <a href="https://github.com/randy3k/SendCode">SendCode</a>.</td>
    </tr>
    <tr>
        <th>Popup Hints</th>
        <th>Code Tools</th>
    </tr>
    <tr>
        <td width="50%">
            <img src="https://user-images.githubusercontent.com/1690993/29746410-325e1ce2-8aa7-11e7-9536-a1202710072f.png" width="100%">
        </td>
        <td width="50%">
            <img src="https://user-images.githubusercontent.com/1690993/29596563-b993db6c-878b-11e7-9fa9-03e25d2ad506.gif" width="80%">
            <br>
            <img src="https://user-images.githubusercontent.com/1690993/29596635-081d6bc2-878c-11e7-8204-aa61683d2792.gif" width="80%">
        </td>
    </tr>
    <tr>
        <td width="50%">[Help] button opens <a href="https://www.rdocumentation.org/">rdocumentation.org</a></td>
        <td width="50%">Format Code and Extract Function</td>
    </tr>
</table>

### Syntaxes

- R Extended Syntax (merged into Sublime Text)
- Rcpp Syntax
- R Sweave and R Markdown syntaxes


### Build commands

Build commands <kbd>C</kbd>+<kbd>b</kbd> for R Package, Rmarkdown and Rnw files.


<img src="https://user-images.githubusercontent.com/1690993/29746375-2b20f496-8aa6-11e7-993a-a253af5d8e44.png" width="300px"></img>

## Installation

- Install via [Package Control](https://sublime.wbond.net)

## Settings

See `Perference: R-Box Settings`

## Recommendations

- [SendCode](https://github.com/randy3k/SendCode) for sending R code to Terminal / R GUI / RStudio.
- [Bracket​Highlighter](https://github.com/facelessuser/BracketHighlighter) for advanced bracket highlighting.
- [Whitespace](https://github.com/randy3k/Whitespace) for cleaning whitespaces.
- [TerminalView](https://github.com/Wramberg/TerminalView) for running R Console in Sublime Text (macOS and Linux only).
- [rtichoke](https://github.com/randy3k/rtichoke) is a better R console for Terminal.

<img src="https://user-images.githubusercontent.com/1690993/29753906-c65dbad2-8b48-11e7-8e02-d6d66bd90e2f.gif" width="700px"></img>

Running `rtichoke` on TerminalView within Sublime Text.