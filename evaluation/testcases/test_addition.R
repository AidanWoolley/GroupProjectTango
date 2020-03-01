source("test_tools.R")

.source_path <- "src/add_two.R"
source(.source_path)

.descriptions <- list(
	add_two = "adds two numbers together"
)

testAddZero <- function() {
    tdk_tested_name <- "add_two"
    tdk_test_description <- "add one and zero together"

    result <- tdk_run(add_two, 1, 0)
    assert_equals(result, 1.0)
    
    return(tdk_return())
}