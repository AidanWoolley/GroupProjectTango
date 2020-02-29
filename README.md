# GroupProjectTango
An automatic code assessment tool for R code for CambridgeSpark

## Running with docker

1. Build the docker image:
```
docker build -t tango .
```
This should be run from the project root. You should now see `tango:latest` when you run:
```
docker images
```

2. Slimify the docker container (optional):
```
docker-slim build --http-probe=false --mount "/tmp/tango:/home/tango/out" --include-path=/tmp --include-path=/usr/lib/R --include-path=/usr/local/lib/R tango
```

This gives us a `tango.slim` image which should be ~5X smaller than the previous image

3. Spin up the docker container:
**TODO: there should be more options to mount input files**
```
docker run -it tango
```
The output can be found in the mounted directory which contains the files to be checked.
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
