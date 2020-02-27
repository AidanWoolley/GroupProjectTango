source("src/add_two.R")
source("test_tools.R")

.descriptions <- list(
	add_two = "adds two numbers together"
)

testAddZero <- function() {
    tdk_tested_name <- "add_two"
    tdk_test_description <- "add one and zero together"

    result <- tdk_run(add_two, 1, 0)
    print(result)
    assert_equals(result, 1.0)
    
    return(tdk_return())
}