source("src/calculate.R")
source("test_tools.R")

testIncrement <- function() {
	tdk_tested_name <- "increment"
	tdk_test_description <- "tests if increment works properly"

	result <- tdk_run(increment, 1)
	assert_equals(result, 2)

	return(tdk_return())
}
