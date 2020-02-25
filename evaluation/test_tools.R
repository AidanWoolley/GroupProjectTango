require('gtools')

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
	if (tdk_status != 2 && (x) != (y)) {
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

# TODO: check if all the variables are defined
tdk_return <- gtools::defmacro(x, y, expr = {
	if (!exists("tdk_info"))
		tdk_info <- ""
	if (!exists("tdk_test_description"))
		tdk_test_description <- ""
	if (!exists("tdk_tested_name")) {
		tdk_tested_name <- ""
		tdk_file_path <- ""
	} else {
		tdk_file_path <- attr(attr(get(tdk_tested_name), "srcref"), "srcfile")$filename
	}

	ret <- list(
		test_description = tdk_test_description,
		file_path = tdk_file_path, # TODO: path to tested function
		test_type = "primary",
		function_tested__name = tdk_tested_name,
		function_tested__description = "" # TODO: tested function description
	)

	# Either a failure or an error
	if (tdk_status != 0) {
		ret[["info"]] <- tdk_info
		ret[["details"]] <- "" # TODO: stacktrace
	}

	# This is a macro, so return is omitted
	list(status = tdk_status, data = ret)
})

# Runs the function fn with arguments <for now only x>
# and captures its errors into environmental tdk_ variables
# TODO: take variable number of arguments
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

tdk_run <- gtools::defmacro(fn, x, expr = {
	tdk_fn_executed <- FALSE

	result <- tryCatch({
			tdk_result <- fn(x)
			tdk_fn_executed = TRUE
			# If we return here, we would go to error (?)
			result
		},
		error = gtools::defmacro(e, expr = {
			return(0)
		})
	)
	if (tdk_fn_executed)
		return(result)
	tdk_status = 2
	tdk_info = "" # TODO: print e
	tdk_details = "" # TODO: stacktrace
	return(0)
})