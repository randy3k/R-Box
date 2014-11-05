# generate completions.json
library(rjson)
library(data.table)
library(ggplot2)

getobjs = function(pkg){
    l = ls(pattern="*", paste0("package:",pkg))
    ind = grep("^[a-zA-Z\\._]+$", l)
    l = l[ind]
    l[nchar(l) > 3]
}

packages = c("base", "stats", "methods", "utils",
    "graphics", "grDevices", "data.table", "ggplot2")

completions = lapply(packages, getobjs)
names(completions) = packages

cat(toJSON(completions), file="completions.json")

l = list()
for (pname in packages){
    pkg = completions[[pname]]
    for (objn in pkg){
        obj = get(objn, envir = as.environment(paste0("package:", pname)))
        if (is.function(obj)){
            body = capture.output(args(obj))[1]
            if (body == "NULL") next
            body = gsub("function ", objn, body)
            l[[objn]] = body
        }
    }
}

cat(toJSON(l), file="hint.json")
