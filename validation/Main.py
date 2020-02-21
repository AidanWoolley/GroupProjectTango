"""For running validation on windows with rpy2."""
from validation.Validation import  Validator
import rpy2
from rpy2.robjects import r
from linter.Linter import Linter
from os.path import abspath

error_linter = '''
library('lintr')
lint("example_linter_input.R", linters=c(object_usage_linter))
'''

failure_linter = '''
library('lintr')
args <- c("example_linter_input.R", "print", "sink")
fileName <- args[1]

my_undesirable_functions <- c()

for (i in 2:length(args)) {
  my_undesirable_functions[[args[[i]]]] <- "restricted function"
}

undesirable_func_linter <- undesirable_function_linter(fun=my_undesirable_functions)

lint(fileName, linters=undesirable_func_linter)
'''

with open("get_libraries.R", "r") as f:
    get_libraries = f.read()

with open("linter_output_errors.txt", "w") as f:
    output = r(error_linter)
    f.write(str(output))

with open("linter_output_failures.txt", "w") as f:
    output = r(failure_linter)
    f.write(str(output))

with open("libraries.txt", "w") as f:
    output = r(get_libraries)
    f.write(str(output))


j = Validator.validate("config.yaml")

print(f"printing the validator output: \n\n {j}")

with open("sample_validation_output.json", "w") as f:
    f.write(j)
