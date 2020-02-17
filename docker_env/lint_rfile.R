library('lintr')
l <- with_defaults(default = default_linters, object_usage_linter=NULL)
print(lint(commandArgs(trailingOnly = TRUE)[1], linters = l))
