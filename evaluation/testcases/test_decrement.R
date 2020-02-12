source("src/calculate.R")
source("test_tools.R")

testDecrementZero <- function() {
    result <- decrement(0)
    return(testEquals(result, -1, "decrement", "testing decrementing zero"))
}

testDecrementOne <- function() {
    result <- decrement(1)
    return(testEquals(result, 0, "decrement"))
}

.tests = c(testDecrementZero, testDecrementOne)
