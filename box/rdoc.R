topic_rd <- function(pkg_name, topic) {
    rd_file <- as.character(help((topic), (pkg_name)))
    utils:::.getHelpFile(rd_file)
}

topic_arguments <- function(rd) {
    ret <- rd[sapply(rd, function(x) attr(x, "Rd_tag") == "\\arguments")]
    if (length(ret) == 0) {
        list()
    } else {
        ret[[1]]
    }
}

parse_arguments <- function(x) {
    out <- list()
    for (d in x) {
        attr(d[[1]][[1]], "Rd_tag") %in% c("TEXT", "\\dots") || next
        out <- c(out, list(parse_argument(d)))
    }
    out
}

parse_argument <- function(x){
    if (attr(x[[1]][[1]], "Rd_tag") == "\\dots") {
        argument_name <- "..."
    } else {
        argument_name <- trimws(as.character(x[[1]][[1]]))
    }
    list(
        arg = argument_name,
        content = parse_text(x[[2]])
    )
}

parse_text <- function(x){
    paste(unlist(x), collapse = "")
}

args <- commandArgs(TRUE)
foo <- topic_rd(args[[1]], args[[2]])
bar <- topic_arguments(foo)
boo <- parse_arguments(bar)
for (b in boo) {
    cat("arg:", b$arg)
    cat("\n")
    cat("content:", gsub("\n", "\\\\n", b$content))
    cat("\n")
}
