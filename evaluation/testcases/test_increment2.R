source("test_tools.R")

tdk_file_path <- "src/calculate.R"
source(tdk_file_path)

.descriptions <- list(
	increment2 = "test while loop"
)

testIncrement2 <- function() {
    tdk_tested_name <- "increment2"
    tdk_test_description <- "test if (0++)++ is 2"

    result <- tdk_run(increment2, 0, timeout = 2)
    assert_equals(result, 2)

    return(tdk_return())
}
