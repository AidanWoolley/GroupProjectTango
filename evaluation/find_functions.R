
find_functions <- function(file) {
    search_env = new.env()
    source(file = file, local = search_env)
    objects = ls(envir = search_env)
    functions = objects[sapply(ls(envir = search_env), FUN = function(x) {
        is.function(get(x, envir = search_env))
    })]
    return(functions)
}
