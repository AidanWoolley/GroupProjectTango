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
		print(test_result$passed)
		# success
		if (test_result$passed == TRUE) {
			new_entry <- list(
				test_name = "name of test function",
				# TODO: test if empty
				test_description = test_result$test_description,
				file_path = "path to file being tested (not the test file)",
				test_type = "primary",
				# TODO: test if empty
				function_tested__name = test_result$function_tested,
				function_tested__description = "description of tested function"
			)
			output_json$runners$successes[[num_success]] <- new_entry
			num_success = num_success + 1
		}
		# failure
		else if (test_result$passed == FALSE) {
			output_json[["passed"]] = FALSE
			new_entry <- list(
				info = "type of assertion that failed",
				details = "stacktrace of failed assertion",
				test_name = "name of test function",
				# TODO: test if empty
				test_description = test_result$test_description,
				file_path = "path to file being tested (not the test file)",
				test_type = "primary",
				# TODO: test if empty
				function_tested__name = test_result$function_tested,
				function_tested__description = "description of tested function"
			)
			output_json$runners$failures[[num_fail]] <- new_entry
			num_fail = num_fail + 1
		}
		# error
		else {
			output_json[["passed"]] = FALSE
			new_entry <- list(
				info = "type and message of occured exception",
				details = "stacktrace of occured exception",
				test_name = "name of test function",
				# TODO: test if empty
				test_description = test_result$test_description,
				file_path = "path to file being tested (not the test file)",
				test_type = "primary (just hard code it as primary for now)",
				# TODO: test if empty
				function_tested__name = test_result$function_tested,
				function_tested__description = "description of tested function, empty string if not found",
				line_number = 0
			)
			output_json$runners$errors[[num_error]] <- new_entry
			num_error = num_error + 1
		}
	}
}
output_json$runners[["tests_run"]] = num_fail + num_success + num_error - 3

# Assuming existence of directory output
fd <- file("output/evaluation_result.json")
writeLines(rjson::toJSON(output_json), fd)
close(fd)
