source("src/calculate.R")
source("test_tools.R")

testMultiplyZero <- function() {
    result <- multiply(0)
    return(testEquals(result, 0, "multiply", "testing multiplication by zero"))
}

testMultiplyOne <- function() {
    result <- multiply(1)
    return(testEquals(result, 30, "multiply"))
}

.tests = c(testMultiplyZero, testMultiplyOne)
