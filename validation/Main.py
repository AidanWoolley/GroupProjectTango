"""For running validation on windows with rpy2."""

from validation.Validation import Validator
import json

import yaml
expected_config = {
            "files": ["file1.R", "file2.R"],
            "restricted_libraries": {
                "file1.R": ["lib1", "lib2", "lib3"],
                "file2.R": ["lib4", "lib5", "lib6"]
            },
            "restricted_functions": {
                "file1.R": ["func1", "func2", "func3"],
                "file2.R": ["func0", "func1", "func2"]
            }
        }

with open("test_validation/config.yaml", "w") as f:
    yaml.dump(expected_config, f)


# libs = Validator._get_libraries()[5:-3].split(",")
#
# print(json.dumps(Validator.validate_file("test_validation/syntax_error.R", [], libs, []), indent=2))


# output = Validator.validate("config.yaml")
# print(output)
# print(Validator._invoke_lintr_error("example_linter_input.R"))
# print(Validator._invoke_lintr_failure("example_linter_input.R", ["print"]))
# print(Validator._get_libraries())



# from validation.Validation import  Validator
# import rpy2
# from rpy2.robjects import r
# from linter.Linter import Linter
# from os.path import abspath
#
# error_linter = '''
# library('lintr')
# lint("example_linter_input.R", linters=c(object_usage_linter))
# '''
#
# failure_linter = '''
# library('lintr')
# args <- c("example_linter_input.R", "print", "sink")
# fileName <- args[1]
#
# my_undesirable_functions <- c()
#
# for (i in 2:length(args)) {
#   my_undesirable_functions[[args[[i]]]] <- "restricted function"
# }
#
# undesirable_func_linter <- undesirable_function_linter(fun=my_undesirable_functions)
#
# lint(fileName, linters=undesirable_func_linter)
# '''
#
# with open("get_libraries.R", "r") as f:
#     get_libraries = f.read()
#
# with open("linter_output_errors.txt", "w") as f:
#     output = r(error_linter)
#     f.write(str(output))
# with open("../test_validation/linter_output_errors.txt", "w") as f:
#     f.write(str(output))
#
# with open("linter_output_failures.txt", "w") as f:
#     output = r(failure_linter)
#     f.write(str(output))
# with open("../test_validation/linter_output_failures.txt", "w") as f:
#     f.write(str(output))
#
# with open("libraries.txt", "w") as f:
#     output = r(get_libraries)
#     f.write(str(output))
# with open("../test_validation/libraries.txt", "w") as f:
#     f.write(str(output))
#
# with open("example_linter_input.R", "r") as f:
#     output = f.read()
# with open("../test_validation/example_linter_input.R", "w") as f:
#     f.write(output)
#
#
# # j = Validator.validate("config.yaml")
# print(Validator._invoke_lintr_error("example_linter_input.R"))
# # print(f"printing the validator output: \n\n {j}")
# #
# # with open("sample_validation_output.json", "w") as f:
# #     f.write(j)
