# shamelessly copy from
# https://github.com/rstudio/rstudio/blob/54cd3abcfc58837b433464c793fe9b03a87f0bb4/src/cpp/session/modules/SessionSource.R

detectFreeVars_Call <- function(e, w) {
    freeVars <- character(0)

    func <- e[[1]]
    funcName <- as.character(func)
    args <- as.list(e[-1])

    if (typeof(func) == "language") {
        freeVars <- c(freeVars, codetools:::walkCode(func, w))
    } else if (funcName %in% c("<-", "<<-", "=", "for") && length(args) > 1 && typeof(args[[1]]) !=
        "language") {
        lvalue <- as.character(args[[1]])

        # Need to walk the right side of an assignment, before considering the lvalue
        # (e.g.: x <- x + 1)
        args <- args[-1]
        if (length(args) > 0) {
            for (ee in args) freeVars <- c(freeVars, codetools:::walkCode(ee, w))
        }
        args <- c()  # Clear out `args` so they aren't walked later

        if (funcName == "<<-")
            assign(lvalue, T, envir = w$assignedGlobals) else assign(lvalue, T, envir = w$assigned)
    } else if (funcName == "$") {
        # In foo$bar, ignore bar
        args <- args[-2]
    } else if (funcName == "function") {
        params <- args[[1]]
        w$assigned <- new.env(parent = w$assigned)

        for (param in names(params)) {
            assign(param, T, envir = w$assigned)
            freeVars <- c(freeVars, codetools:::walkCode(params[[param]], w))
        }
        args <- args[-1]
    }

    if (length(args) > 0) {
        for (ee in args) freeVars <- c(freeVars, codetools:::walkCode(ee, w))
    }
    return(unique(freeVars))
}

detectFreeVars_Leaf <- function(e, w) {
    if (typeof(e) == "symbol" && nchar(as.character(e)) > 0 && !exists(as.character(e),
        envir = w$assigned))
        return(as.character(e)) else return(character(0))
}

detect_free_vars <- function(file) {
    globals <- new.env(parent = emptyenv())

    # Ignore predefined symbols like T and F
    assign("T", T, envir = globals)
    assign("F", T, envir = globals)

    w <- codetools:::makeCodeWalker(assigned = globals, assignedGlobals = globals,
        call = detectFreeVars_Call, leaf = detectFreeVars_Leaf)
    freeVars <- character(0)
    for (e in parse(file)) freeVars <- c(freeVars, codetools:::walkCode(e,
        w))
    return(unique(freeVars))
}

for (var in detect_free_vars(file('stdin'))) {
    cat(var, "\n")
}
