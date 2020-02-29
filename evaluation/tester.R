require('rjson')
require('yaml')

source('find_functions.R')

evaluator <- function(out_path) {
	output_json <- list(
		passed = TRUE
	)

	num_success <- 1
	num_fail <- 1
	num_error <- 1

	config_yaml <- read_yaml("config.yaml")

	for (current_test_file in config_yaml[["tests"]]) {
		source(current_test_file)

		.tests <- find_functions(current_test_file)

		for (current_test in .tests) {
			if(substring(current_test, 1, 1) == ".")
				next

			test_result <- get(current_test)()
			# success
			if (test_result$status == 0) {
				output_json$runners[[1]]$successes[[num_success]] <- test_result$data
				output_json$runners[[1]]$successes[[num_success]]$test_name <- current_test

				if(exists('.descriptions')) {
					if(!is.null(.descriptions[test_result$data$function_tested__name][[1]]))
						output_json$runners[[1]]$successes[[num_success]]$function_tested__description <- .descriptions[test_result$data$function_tested__name][[1]]
					else
						output_json$runners[[1]]$successes[[num_success]]$function_tested__description <- "" 
				}

				num_success = num_success + 1
			}
			# failure
			else if (test_result$status == 1) {
				output_json[["passed"]] = FALSE
				output_json$runners[[1]]$failures[[num_fail]] <- test_result$data
				output_json$runners[[1]]$failures[[num_fail]]$test_name <- current_test

				if(exists('.descriptions')) {
					if(!is.null(.descriptions[test_result$data$function_tested__name][[1]]))
						output_json$runners[[1]]$failures[[num_fail]]$function_tested__description <- .descriptions[test_result$data$function_tested__name][[1]]
					else
						output_json$runners[[1]]$failures[[num_fail]]$function_tested__description <- "" 
				}

				num_fail = num_fail + 1
			}
			# error
			else {
				output_json[["passed"]] = FALSE
				output_json$runners[[1]]$errors[[num_error]] <- test_result$data
				output_json$runners[[1]]$errors[[num_error]]$test_name <- current_test

				if(exists('.descriptions')) {
					if(!is.null(.descriptions[test_result$data$function_tested__name][[1]]))
						output_json$runners[[1]]$errors[[num_error]]$function_tested__description <- .descriptions[test_result$data$function_tested__name][[1]]
					else
						output_json$runners[[1]]$errors[[num_error]]$function_tested__description <- "" 
				}

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
	output_json$runners[[1]][["runner_key"]] <- "testcases"

	# Assuming existence of directory output
	fd <- file(out_path)
	writeLines(rjson::toJSON(output_json), fd)
	close(fd)
}

evaluator("out/evaluation.json")
