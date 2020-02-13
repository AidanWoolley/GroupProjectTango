require('rjson')

output_json <- list(
	runners = list(
		successes = list(),
		failures = list(),
		errors = list(),
		runner_key = "testcases",
		tests_run = 0
	),
	passed = TRUE
)

num_success <- 1
num_fail <- 1
num_error <- 1
test_files <- list.files(path="testcases")
for (current_test_file in test_files) {
	# TODO: use something else
	source(paste("testcases/", current_test_file, sep=""))

	print(c("File: ", current_test_file))
	for (current_test in .tests) {
		test_result <- current_test()
		# success
		if (test_result$status == 0) {
			output_json$runners$successes[[num_success]] <- test_result$data
			num_success = num_success + 1
		}
		# failure
		else if (test_result$status == 1) {
			output_json[["passed"]] = FALSE
			output_json$runners$failures[[num_fail]] <- test_result$data
			num_fail = num_fail + 1
		}
		# error
		else {
			output_json[["passed"]] = FALSE
			output_json$runners$errors[[num_error]] <- test_result$data
			num_error = num_error + 1
		}
	}
}
output_json$runners[["tests_run"]] = num_fail + num_success + num_error - 3

# Assuming existence of directory output
fd <- file("output/evaluation_result.json")
writeLines(rjson::toJSON(output_json), fd)
close(fd)
