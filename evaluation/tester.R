# TODO 
# gather the tests, apply them
# build json

test_files <- list.files(path="testcases")
for (current_test_file in test_files) {
    source(paste("testcases/", current_test_file, sep=""))

    for (current_test in .tests) {
        print(current_test())
    }
}