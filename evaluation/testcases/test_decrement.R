source("src/calculate.R")
source("test_tools.R")

testDecrementZero <- function() {
    result <- decrement(0)
	assert_equals(result, -1)
	tdk_return()
}

testDecrementOne <- function() {
    result <- decrement(1)
	assert_equals(result, 0)
	tdk_return()
}

.tests = c(testDecrementZero, testDecrementOne)
