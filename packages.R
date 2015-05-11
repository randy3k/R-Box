library(RJSONIO)
library(pryr)
library(stringr)
library(methods)

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
    for (x in l){
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

args <- commandArgs(TRUE)

if (length(args)>0){
    packages <- args
}else{
    packages <- c(
        "base",
        "data.table",
        "devtools",
        "doParallel",
        "dplyr",
        "foreach",
        "ggplot2",
        "graphics",
        "grDevices",
        "httr",
        "knitr",
        "MASS",
        "Matrix",
        "methods",
        "plyr",
        "reshape2",
        "stats",
        "utils"
    )
}

for (pkg in packages){
    library(pkg, character.only=TRUE)
    objects <- ls_package(pkg)
    objects_omit_s3 <- omit_s3(pkg, objects)
    functions <- get_functions(pkg, objects)
    bodies <- get_body(pkg, functions)

    output <- list(objects=objects_omit_s3, methods=bodies)
    cat(toJSON(output, pretty=TRUE), file =file.path("packages", paste0(pkg, ".json")))
}
