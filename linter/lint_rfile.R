#! /usr/bin/Rscript
args <- commandArgs(trailingOnly = TRUE)
fn <- args[1]
library('lintr')
objs = lint(fn)
sink('__linter_output__.txt');
print(objs);
sink()
