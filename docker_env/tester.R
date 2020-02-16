require('rjson')

evaluator <- function(out_path) {
	output_json <- list(
		passed = TRUE
	)

	num_success <- 1
	num_fail <- 1
	num_error <- 1
	test_files <- list.files(path="tests")
	for (current_test_file in test_files) {
		# TODO: use something else
		source(paste("tests/", current_test_file, sep=""))

		for (current_test in .tests) {
			test_result <- current_test()
			# success
			if (test_result$status == 0) {
				output_json$runners[[1]]$successes[[num_success]] <- test_result$data
				num_success = num_success + 1
			}
			# failure
			else if (test_result$status == 1) {
				output_json[["passed"]] = FALSE
				output_json$runners[[1]]$failures[[num_fail]] <- test_result$data
				num_fail = num_fail + 1
			}
			# error
			else {
				output_json[["passed"]] = FALSE
				output_json$runners[[1]]$errors[[num_error]] <- test_result$data
				num_error = num_error + 1
			}
		}
	}
	tests_run <- num_fail + num_success + num_error - 3
	if (tests_run == 0) {
		# This doesn't make sense, alert the developer
		stop("zero tests supplied")
	}

	output_json$runners[[1]][["tests_run"]] <- tests_run
	# If we put initial runners to be an empty list, R will just contract initial
	# That's why we put runner_key here
	output_json$runners[[1]][["runner_key"]] <- "tests"

	# Assuming existence of directory output
	fd <- file(out_path)
	writeLines(rjson::toJSON(output_json), fd)
	close(fd)
}

evaluator("out/evaluation_result.json")
