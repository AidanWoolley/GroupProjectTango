library('lintr')
print(lint(commandArgs(trailingOnly = TRUE)[1], linters=c(object_usage_linter)))