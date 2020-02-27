source("src/calculate.R")
source("test_tools.R")

.descriptions <- list(
	multiply = "multiplies by 30"
)

.helper <- function() {
	return(0)
}

testMultiplyZero <- function() {
    tdk_test_description <- "testing multiplication by zero"
	tdk_tested_name <- "multiply"

    result <- tdk_run(multiply, 0)
	assert_equals(result, 0)

	return(tdk_return())
}

testMultiplyOne <- function() {
	tdk_test_description <- "testing multiplication by 1"
	tdk_tested_name <- "multiply"

    result <- tdk_run(multiply, 1)
	assert_equals(result, 30)

	return(tdk_return())
}

testMultiplyType <- function() {
	# Basically annotations
	tdk_tested_name = "multiply"
	tkd_test_description = "check if return type of multiply is correct"
	# Actual code
	result <- tdk_run(multiply, as.integer(1))
	expected <- as.integer(30)
	assert_equals(result, expected)
	assert_same_type(result, expected)


	return(tdk_return())
}
