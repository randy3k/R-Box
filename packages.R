library(RJSONIO)
library(pryr)
library(stringr)
library(methods)

args <- commandArgs(TRUE)

if (length(args)>0){
    packages <- args
}else{
    packages <- c(
        "base",
        "graphics",
        "grDevices",
        "methods",
        "stats",
        "utils"
    )
}

ls_package <- function(pkg){
    l <- ls(pattern="*", paste0("package:",pkg))
    ind <- grep("^[a-zA-Z\\._]+$", l)
    l <- l[ind]
    l[nchar(l) >= 3]
}

omit_s3 <- function(pkg, l){
    e <- as.environment(paste0("package:", pkg))
    l[sapply(l, function(x) {
        obj <- get(x, envir = e)
        !is.function(obj) || !is_s3_method(x)
    })]
}

get_functions <- function(pkg, l){
    e <- as.environment(paste0("package:", pkg))
    l[sapply(l, function(x) {
        obj <- get(x, envir = e)
        is.function(obj)
    })]
}

get_body <- function(pkg, l){
    e <- as.environment(paste0("package:", pkg))
    out <- list()
    for (x in l){
        obj <- get(x, envir = e)
        if (is.function(obj)){
            ## using deparse instead of capture.output
            ## head(., -1) removes the "NULL" output from args()
            body <- head(deparse(args(obj)), -1)
            if (!length(body))
                next
            body[[1]] <- sub("^function ", x, body[[1]])
            ## collapse multi-line bodies using paste, but first removing superfluous
            ##   spaces at start of subsequent lines
            if (length(body) > 1)
                body <- paste(sub("^    ", "", body), collapse="")
            out[[x]] <- body
        }
    }
    out
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
