library(RJSONIO)

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
    members <- ls(pattern="*", paste0("package:",pkg))
    ind <- grep("^[a-zA-Z\\._][0-9a-zA-Z\\._]+$", members)
    out <- members[ind]
    attr(out, "package") <- pkg
    out
}

get_functions <- function(objs){
    pkg <- attr(objs, "package")
    e <- as.environment(paste0("package:", pkg))
    out <- Filter(function(x) {
            obj <- get(x, envir = e)
            is.function(obj)
        },
        objs
    )
    attr(out, "package") <- pkg
    out
}

get_body <- function(fname, env = parent.frame()){
    f <- get(fname, env = env)
    if (is.function(f)){
        body <- head(deparse(args(f)), -1)
        if (length(body) > 0){
            body[[1]] <- sub("^function ", fname, body[[1]])
            if (length(body) > 1){
                body <- paste(sub("^    ", "", body), collapse="")
            }
            return(body)
        }
    }
    return(NULL)
}

get_bodies <- function(functions){
    pkg <- attr(functions, "package")
    e <- as.environment(paste0("package:", pkg))
    out <- list()
    for (f in functions){
        body <- get_body(f, e)
        if (!is.null(body)){
            out[[f]] <- body
        }
    }
    out
}

dir.create("packages", FALSE)

for (pkg in packages){
    library(pkg, character.only=TRUE)
    objects <- ls_package(pkg)
    functions <- get_functions(objects)
    bodies <- get_bodies(functions)

    output <- list(objects=objects, methods=bodies)
    cat(toJSON(output, pretty=TRUE), file =file.path("packages", paste0(pkg, ".json")))
}
