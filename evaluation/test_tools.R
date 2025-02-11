require('gtools')
require('R.utils')

source('find_functions.R')

# We use a macro instead of a function because we
# want to capture environment of the calling
# function.
#
# Alternative would be
#    if (!assert_equals(x, y))
#       return 'fail'
# Note that something like
#    assert_equals(&return_value, x, y)
# isn't trivially achievable since R can't pass
# primitives by reference
#
# Ideally, a macro would be able to return a value
# inside the original function, but that doesn't
# seem to be possible


assert_equals <- gtools::defmacro(x, y, expr = {
	if (!exists("tdk_status"))
		tdk_status = 0
	if (is.null(x) && !is.null(y)) {
		tdk_info <- "unexpected result (got null)"
		tdk_status <- 1
	}
	else if (!is.null(x) && is.null(y)) {
		tdk_info <- "unexpected result (didn't get null)"
		tdk_status <- 1
	}
	else if (tdk_status != 2 && (x) != (y)) {
		tdk_info <- "unexpected result"
		tdk_status <- 1
	}
})

assert_less_than <- gtools::defmacro(x, y, expr = {
	if (!exists("tdk_status"))
		tdk_status = 0
	if (tdk_status != 2 && (x) >= (y)) {
		tdk_info <- "unexpected result"
		tdk_status <- 1
	}
})

assert_same_type <- gtools::defmacro(x, y, expr = {
	if (!exists("tdk_status"))
		tdk_status <- 0
	if (tdk_status != 2 && typeof(x) != typeof(y)) {
		tdk_info <- "wrong type"
		tdk_status <- 1
	}
})

tdk_return <- gtools::defmacro(x, y, expr = {
	if (!exists("tdk_info"))
		tdk_info <- ""
	if (!exists("tdk_details"))
		tdk_details <- ""
	if (!exists("tdk_test_description"))
		tdk_test_description <- ""
	if (!exists("tdk_tested_name"))
		tdk_tested_name <- ""
	if (!exists("tdk_file_path")) 
		tdk_file_path <- ""

	ret <- list(
		test_description = tdk_test_description,
		file_path = tdk_file_path,
		test_type = "primary",
		function_tested__name = tdk_tested_name
	)

	# Either a failure or an error
	if (tdk_status != 0) {
		ret[["info"]] <- tdk_info
		ret[["details"]] <- tdk_details
	}

	# This is a macro, so return is omitted
	list(status = tdk_status, data = ret)
})

# Runs the function fn with arguments <for now only x>
# and captures its errors into environmental tdk_ variables
# TODO: this is a horrible implementation
# For some reason
#     tryCatch({
#         if (rng() % 2 == 0)
#           stop("an error")
#         return(1)
#       },
#       error = function(e) {
#          return(2)
#       }
#     )
# always returns 2
tdk_run <- gtools::defmacro(fn, DOTS, timeout = 1.0, expr = {
	tdk_fn_executed <- FALSE

	result <- tryCatch({
			# TODO: replace silent with something nicer
			tdk_result <- withTimeout(fn(...), timeout = timeout, onTimeout = "silent")
			tdk_fn_executed = TRUE
			# If we return here, we would go to error (?)
			list(calculation = tdk_result, details = "", info = "")
		},
		error = gtools::defmacro(e, expr = {
			return(list(calculation = 0, details = paste(unlist(capture.output(traceback(e))), collapse = '\n'), info = typeof(e)))
			return(0)
		})
	)

	if (tdk_fn_executed)
		return(result$calculation)
	tdk_status = 2
	tdk_info = result$info
	tdk_details = result$details
	return(0)
})
