source("src/calculate.R")
source("test_tools.R")

testDecrementZero <- function() {
	tdk_tested_name <- "decrement"
	tdk_test_description <- "testing whether decrementing 0 yields -1"

    result <- tdk_run(decrement, 0)
	assert_equals(result, -1)

	return(tdk_return())
}

testDecrementOne <- function() {
	tdk_tested_name <- "decrement"
	tdk_test_description <- "testing whether decrementing 1 yields 0"

    result <- tdk_run(decrement, 1)
	assert_equals(result, 0)

	return(tdk_return())
}

testDecrementUndocumented <- function() {
	result <- tdk_run(decrement, 2)
	assert_equals(result, 1)

	return(tdk_return())
}
