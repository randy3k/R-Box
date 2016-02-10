library(stringr)

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

template <- "
    - match: \\b(foo)\\s*(\\()
      scope: meta.function-call.r
      captures:
        1: support.function.r
        2: punctuation.definition.parameters.r
      push:
        - meta_content_scope: meta.function-call.parameters.r
        - match: (?<=\\(|,|^)\\s*([a-zA-Z._][a-zA-Z0-9._]*)(?=\\s*(?:\\)|=[^=]|,|\\n))
          captures:
            1: variable.parameter.r
        - match: \\)
          pop: true
        - include: \"R Extended.sublime-syntax\"
"

templated_block <- function(pkg){
    content <- paste0(sub("\\.","\\\\\\\\.", get_functions(ls_package(pkg))), collapse="|")
    str_replace(template, "foo", content)
}

dict <- ""
for (pkg in packages){
    library(pkg, character.only=TRUE)
    dict <- paste0(dict, templated_block(pkg))
}

syntax_file <- "syntax/R Support Function.sublime-syntax"
content <- readChar(syntax_file, file.info(syntax_file)$size)
begin_pt <- str_locate(content, "main:\n")[2]
str_sub(content, begin_pt, str_length(content)) <- dict

dir.create("syntax", FALSE)
cat(content, file=syntax_file)
