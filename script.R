library(RJSONIO)
library(pryr)
library(stringr)

library(data.table)
library(ggplot2)
library(foreach)

ls_package <- function(pkg){
    l <- ls(pattern="*", paste0("package:",pkg))
    ind <- grep("^[a-zA-Z\\._]+$", l)
    l <- l[ind]
    l[nchar(l) >= 3]
}


omit_s3 <- function(pkg, l){
    l[sapply(l, function(x) {
        obj <- get(x, envir = as.environment(paste0("package:", pkg)))
        !is.function(obj) || !is_s3_method(x)
    })]
}

get_functions <- function(pkg, l){
    l[sapply(l, function(x) {
        obj <- get(x, envir = as.environment(paste0("package:", pkg)))
        is.function(obj)
    })]
}

get_body <- function(pkg, l){
    out <- list()
    for(x in l){
        obj <- get(x, envir = as.environment(paste0("package:", pkg)))
        if (is.function(obj)){
            body <- capture.output(args(obj))[1]
            if (body == "NULL") next
            body <- gsub("function ", x, body)
            out[[x]] <- body
        }
    }
    out
}

packages <- c(
    "base",
    "stats",
    "methods",
    "utils",
    "graphics",
    "grDevices",
    "data.table",
    "ggplot2",
    "foreach"
)

# completions.json
objs <- lapply(packages, ls_package)
completions <- lapply(1:length(packages), function(i) omit_s3(packages[i], objs[[i]]))
names(completions) <- packages
cat(toJSON(completions, pretty=TRUE), file="support/completions.json")

# hint.json

funcs <- lapply(1:length(packages), function(i) get_functions(packages[i], objs[[i]]))
funcs_body <- lapply(1:length(packages), function(i) get_body(packages[i], funcs[[i]]))
names(funcs_body) <- packages
cat(toJSON(funcs_body, pretty = TRUE), file ="support/hint.json")

# R Extended.tmLanguage

template <-
"\t\t\t\t<dict>
\t\t\t\t\t<key>begin</key>
\t\t\t\t\t<string>\\b(foo)\\s*(\\()</string>
\t\t\t\t\t<key>beginCaptures</key>
\t\t\t\t\t<dict>
\t\t\t\t\t\t<key>1</key>
\t\t\t\t\t\t<dict>
\t\t\t\t\t\t\t<key>name</key>
\t\t\t\t\t\t\t<string>support.function.r</string>
\t\t\t\t\t\t</dict>
\t\t\t\t\t\t<key>2</key>
\t\t\t\t\t\t<dict>
\t\t\t\t\t\t\t<key>name</key>
\t\t\t\t\t\t\t<string>punctuation.definition.parameters.r</string>
\t\t\t\t\t\t</dict>
\t\t\t\t\t</dict>
\t\t\t\t\t<key>comment</key>
\t\t\t\t\t<string>base</string>
\t\t\t\t\t<key>contentName</key>
\t\t\t\t\t<string>meta.function-call.arguments.r</string>
\t\t\t\t\t<key>end</key>
\t\t\t\t\t<string>(\\))</string>
\t\t\t\t\t<key>endCaptures</key>
\t\t\t\t\t<dict>
\t\t\t\t\t\t<key>1</key>
\t\t\t\t\t\t<dict>
\t\t\t\t\t\t\t<key>name</key>
\t\t\t\t\t\t\t<string>punctuation.definition.parameters.r</string>
\t\t\t\t\t\t</dict>
\t\t\t\t\t</dict>
\t\t\t\t\t<key>name</key>
\t\t\t\t\t<string>meta.function-call.r</string>
\t\t\t\t\t<key>patterns</key>
\t\t\t\t\t<array>
\t\t\t\t\t\t<dict>
\t\t\t\t\t\t\t<key>include</key>
\t\t\t\t\t\t\t<string>$self</string>
\t\t\t\t\t\t</dict>
\t\t\t\t\t</array>
\t\t\t\t</dict>
"

get_block <- function(pkg){
    content <- paste0(sub("\\.","\\\\\\\\.", get_functions(pkg, ls_package(pkg))), collapse="|")
    str_replace(template, "foo", content)
}

dict <- ""
for (pkg in packages){
    dict <- paste0(dict, get_block(pkg))
}

syntax_file <- "syntax/R Extended.tmLanguage"
content <- readChar(syntax_file, file.info(syntax_file)$size)
dict_begin <- str_locate(content,
    "<key>support_function</key>\\s*<dict>\\s*<key>patterns</key>\\s*<array>\\s*\n")[2]
dict_end <- str_locate(content, "\n\\s*</array>\\s*</dict>\\s*</dict>\\s*<key>scopeName</key>")[1]

str_sub(content, dict_begin + 1, dict_end) <- dict
cat(content, file=syntax_file)
