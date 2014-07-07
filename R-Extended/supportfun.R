# load and modify 'R Extended.tmLanguage'
require(rjson)

library(data.table)
library(ggplot2)

template = structure(list(
    begin = "\\b(###)\\s*(\\()", end = "(\\))", name = "meta.function-call.r",
    contentName = "meta.function-call.arguments.r", comment = "base",
    patterns = list(structure(list(include = "$self"), .Names = "include")),
    beginCaptures = structure(list(`2` = structure(list(name = "punctuation.definition.parameters.r"), .Names = "name"), `1` = structure(list(name = "support.function.r"), .Names = "name")), .Names = c("2", "1")),
    endCaptures = structure(list(`1` = structure(list(name = "punctuation.definition.parameters.r"), .Names = "name")), .Names = "1")
    ),
    .Names = c("begin", "end", "name", "contentName", "comment", "patterns", "beginCaptures", "endCaptures")
)
filter = function(l){
    ind = grep("^[a-zA-Z\\._]+$", l)
    l[ind]
}
getfuns = function(pkg){
    filter(ls(pattern="*", paste0("package:",pkg)))
}
getregexp = function(pkg){
    s = template
    content = paste0(sub("\\.","\\\\.",getfuns(pkg)),collapse="|")
    s$begin = paste0("\\b(", content, ")\\s*(\\()")
    s
}

packages = c("base", "stats", "methods", "utils",
    "graphics", "grDevices", "data.table", "ggplot2")

m = fromJSON(file="R Extended.tmLanguage.JSON")
m$repository$support_function$patterns = lapply(packages, getregexp)
cat(toJSON(m), file="R Extended.tmLanguage.JSON")
