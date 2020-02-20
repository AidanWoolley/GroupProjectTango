library('lintr')
args <- commandArgs(trailingOnly = TRUE)
fileName <- args[1]

my_undesirable_functions <- c()

for (i in 2:length(args)) {
  my_undesirable_functions[[args[[i]]]] <- "restricted function"
}

undesirable_func_linter <- undesirable_function_linter(fun=my_undesirable_function)

print(lint(fileName, linters=undesirable_func_linter))