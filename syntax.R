library(stringr)

packages <- c(
    "base",
    "graphics",
    "grDevices",
    "methods",
    "stats",
    "utils"
)

get_functions <- function(pkg) {
    objs <- getNamespaceExports(asNamespace(pkg))
    objs <- objs[str_detect(objs, "^[a-zA-Z\\._][0-9a-zA-Z\\._]*$")]
    out <- c()
    for (obj in objs){
        try({
            if (eval(parse(text = paste0("is.function(", pkg, "::", obj, ")")))){
                out <- c(out, obj)
            }
        },
        silent = TRUE)
    }
    out
}


template <- "
    - match: \\b(foo)\\s*(\\()
      captures:
        1: support.function.r
      push:
        - meta_scope: meta.function-call.r
        - meta_content_scope: meta.function-call.parameters.r
        - match: '[a-zA-Z._][a-zA-Z0-9._]*(?=\\s*=)'
          scope: variable.parameter.r
        - match: '(?==)'
          push:
            - include: \"R Extended.sublime-syntax\"
            - match: (?=[,)])
              pop: true
        - match: \\)
          pop: true
        - include: \"R Extended.sublime-syntax\"
"

templated_block <- function(pkg){
    content <- paste0(sub("\\.", "\\\\\\\\.", get_functions(pkg)), collapse = "|")
    str_replace(template, "foo", content)
}

dict <- ""
for (pkg in packages){
    dict <- paste0(dict, templated_block(pkg))
}

syntax_file <- "syntax/R Support Functions.sublime-syntax"
content <- readChar(syntax_file, file.info(syntax_file)$size)
begin_pt <- str_locate(content, "main:\n")[2]
str_sub(content, begin_pt, str_length(content)) <- dict
cat(content, file = syntax_file)
