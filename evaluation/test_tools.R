require('gtools')

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
	if ((x) != (y)) {
		tdk_info <- "unexpected result"
		tdk_status <- 1
	}
})

assert_same_type <- gtools::defmacro(x, y, expr = {
	if (!exists("tdk_status"))
		tdk_status <- 0
	if (typeof(x) != typeof(y)) {
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
	if (!exists("tdk_tested_name"))
		tdk_tested_name <- ""

	ret <- list(
		test_name = "", # TODO: name of the tester function
		test_description = tdk_test_description,
		file_path = "", # TODO: path to tested function
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

testEquals <- function(passed_value, intended_value, function_tested, test_description="") {

    pass <- TRUE
    if (passed_value != intended_value) {
        pass <- FALSE
    }

    return(list(passed = pass, function_tested = function_tested, test_description = test_description))
}
