library(stringr)

args <- commandArgs(TRUE)

if (length(args)>0){
    packages <- args
}else{
    packages <- c(
        "base",
        "stats",
        "methods",
        "utils",
        "graphics",
        "grDevices"
    )
}

ls_package <- function(pkg){
    l <- ls(pattern="*", paste0("package:",pkg))
    ind <- grep("^[a-zA-Z\\._]+$", l)
    l <- l[ind]
    l[nchar(l) >= 3]
}

get_functions <- function(pkg, l){
    l[sapply(l, function(x) {
        obj <- get(x, envir = as.environment(paste0("package:", pkg)))
        is.function(obj)
    })]
}

template <-
"\t\t<dict>
\t\t\t<key>begin</key>
\t\t\t<string>\\b(foo)\\s*(\\()</string>
\t\t\t<key>beginCaptures</key>
\t\t\t<dict>
\t\t\t\t<key>1</key>
\t\t\t\t<dict>
\t\t\t\t\t<key>name</key>
\t\t\t\t\t<string>support.function.r</string>
\t\t\t\t</dict>
\t\t\t\t<key>2</key>
\t\t\t\t<dict>
\t\t\t\t\t<key>name</key>
\t\t\t\t\t<string>punctuation.definition.parameters.r</string>
\t\t\t\t</dict>
\t\t\t</dict>
\t\t\t<key>comment</key>
\t\t\t<string>base</string>
\t\t\t<key>contentName</key>
\t\t\t<string>meta.function-call.arguments.r</string>
\t\t\t<key>end</key>
\t\t\t<string>(\\))</string>
\t\t\t<key>endCaptures</key>
\t\t\t<dict>
\t\t\t\t<key>1</key>
\t\t\t\t<dict>
\t\t\t\t\t<key>name</key>
\t\t\t\t\t<string>punctuation.definition.parameters.r</string>
\t\t\t\t</dict>
\t\t\t</dict>
\t\t\t<key>name</key>
\t\t\t<string>meta.function-call.r</string>
\t\t\t<key>patterns</key>
\t\t\t<array>
\t\t\t\t<dict>
\t\t\t\t\t<key>include</key>
\t\t\t\t\t<string>#function-call-parameter</string>
\t\t\t\t</dict>
\t\t\t\t<dict>
\t\t\t\t\t<key>include</key>
\t\t\t\t\t<string>source.r</string>
\t\t\t\t</dict>
\t\t\t</array>
\t\t</dict>
"

get_block <- function(pkg){
    content <- paste0(sub("\\.","\\\\\\\\.", get_functions(pkg, ls_package(pkg))), collapse="|")
    str_replace(template, "foo", content)
}

dict <- ""
for (pkg in packages){
    library(pkg, character.only=TRUE)
    dict <- paste0(dict, get_block(pkg))
}

syntax_file <- "syntax/R Functions.tmLanguage"
content <- readChar(syntax_file, file.info(syntax_file)$size)
dict_begin <- str_locate(content,
    "<key>patterns</key>\\s*<array>\\s*\n")[2]
dict_end <- str_locate(content, "\n\\s*</array>\\s*<key>repository</key>")[1]

str_sub(content, dict_begin + 1, dict_end) <- dict
cat(content, file=syntax_file)
