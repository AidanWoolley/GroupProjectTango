
testEquals <- function(passed_value, intended_value, function_tested, test_description="") {

    pass <- TRUE
    if (passed_value != intended_value) {
        pass <- FALSE 
    }

    return(list(passed = pass, function_tested = function_tested, test_description = test_description))
}
