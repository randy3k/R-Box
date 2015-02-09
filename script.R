# completions.json
library(RJSONIO)
library(data.table)
library(ggplot2)

getobjs <- function(pkg){
    l <- ls(pattern="*", paste0("package:",pkg))
    ind <- grep("^[a-zA-Z\\._]+$", l)
    l <- l[ind]
    l[nchar(l) > 3]
}

packages <- c("base", "stats", "methods", "utils",
    "graphics", "grDevices", "data.table", "ggplot2")

completions <- lapply(packages, getobjs)
names(completions) <- packages

cat(toJSON(completions, pretty=TRUE), file="support/completions.json")

# hint.json

l <- list()
for (pname in packages){
    pkg <- completions[[pname]]
    for (objn in pkg){
        obj <- get(objn, envir = as.environment(paste0("package:", pname)))
        if (is.function(obj)){
            body <- capture.output(args(obj))[1]
            if (body == "NULL") next
            body <- gsub("function ", objn, body)
            l[[objn]] <- body
        }
    }
}

cat(toJSON(l, pretty = TRUE), file ="support/hint.json")

# R Extended.tmLanguage

library(stringr)

f <- "syntax/R Extended.tmLanguage"
str <- readChar(f, file.info(f)$size)
dict_begin <- str_locate(str,
    "<key>support_function</key>\\s*<dict>\\s*<key>patterns</key>\\s*<array>\\s*\n")[2]
dict_end <- str_locate(str, "\n\\s*</array>\\s*</dict>\\s*</dict>\\s*<key>scopeName</key>")[1]

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

getfuns <- function(pkg){
    l <- ls(pattern="*", paste0("package:",pkg))
    ind <- grep("^[a-zA-Z\\._]+$", l)
    l <- l[ind]
    l <- l[nchar(l) > 3]
    ind <- rep(TRUE, length(l))
    for (i in seq_along(l)){
        obj <- get(l[i], envir = as.environment(paste0("package:", pkg)))
        ind[i] <- is.function(obj)
    }
    l[ind]
}
getregexp <- function(pkg){
    content <- paste0(sub("\\.","\\\\\\\\.", getfuns(pkg)),collapse="|")
    str_replace(template, "foo", content)
}

library(data.table)
library(ggplot2)

packages <- c("base", "stats", "methods", "utils", "graphics", "grDevices", "data.table", "ggplot2")

dict <- ""
for (pkg in packages){
    dict <- paste0(dict, getregexp(pkg))
}
str_sub(str, dict_begin + 1, dict_end) <- dict
cat(str, file="syntax/R Extended.tmLanguage")
