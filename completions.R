# generate completions.json
library(rjson)
library(data.table)
library(ggplot2)
filter = function(l){
    ind = grep("^[a-zA-Z\\._]+$", l)
    l[ind]
}
getfuns = function(pkg){
    filter(ls(pattern="*", paste0("package:",pkg)))
}

packages = c("base", "stats", "methods", "utils",
    "graphics", "grDevices", "data.table", "ggplot2")

completions = lapply(packages, getfuns)
names(completions) = packages

cat(toJSON(completions), file="completions.json")
