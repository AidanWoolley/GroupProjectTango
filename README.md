# GroupProjectTango
An automatic code assessment tool for R code for CambridgeSpark

## SDK guide
Here is a brief guide to writing testcases for an exercise:
- The user must list all of the files containing tests in config.yaml
- Multiple test files can test the same source file, but a single test file can not test multiple source files
- Functions defined in a test file that begin with the character '.' will be ignored by the evaluator and considered helper functions
- Every test function has to define two variables:
  - "tdk_tested_name": a string holding the name of the method tested by this function
  - "tdk_test_description": a string holding a description of the current test function (optional)
- Also, every test file: 
  - Has to source the intended file to be tested and the file "test_tools.R"
  - Can contain a list object that maps source file function names to their description
- Writing a test function:
  - First, a call to tdk_run is made with the intended function and its arguments: tdk_run(fun, argument1, argument2, ...)
  - This call's return value is stored in a variable, which is the result
  - This can be modified by the function and then tested using one of the three assert functions provided: assert_equals, assert_less_than and assert_same_type
  - Note: a single test function can call assert multiple times --- these will be considered different tests
  - Finally, the test function ends with a call to return(tdk_return()) 

## Dependencies
R dependencies

 - rjson
 - yaml
 - gtools
