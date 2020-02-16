library('lintr')
l <- with_default(default = default_linters, object_usgae_linter=NULL)
print(lint(commandArgs(trailingOnly = TRUE)[1], linters = l))
