"""This class takes the static analysis from produces output in relevant format."""
import json
import os
import re

from os.path import isfile, abspath, join as joinpath, dirname
from string import whitespace

from .Linter import Linter

__author__ = "Anish_Das_ad945"

PATH = os.getcwd() + '/validation'


class Validator(Linter):
    """The class uses the static analysis performed by Linter to produce required JSON."""

    @staticmethod
    def _get_installed_libraries():
        """
        Runs an R script to return all the installed.packages() on the machine.

        Returns:
        (list[str]): All the available libraries on the machine.
        """
        lib_list_string = Validator._invoke_R("installed.packages()[, c()]")

        # List is 1 lib per line, awkwardly padded and starting with a blank line
        return [lib.strip() for lib in lib_list_string.splitlines()][1:]

    @staticmethod
    def _invoke_lintr_restricted_functions(file_to_check, restricted_functions):
        """
        Specialized lintr call to only highlight the use of restricted functions.

        Params:
            file_to_check (str): the file to check use of any restricted functions in.
            restricted_functions (list[str]): functions which `file_to_check` must not use.

        Returns:
            (str) Lintr output containing errors for each inappropriate function use.
        """
        if not isfile(file_to_check):
            raise FileNotFoundError(file_to_check)
        restricted_functions_string = ', '.join([f'"{fun}"=""' for fun in restricted_functions])
        undesirable_functions_linter = f'undesirable_function_linter(c({restricted_functions_string}))'
        return Validator._invoke_lintr(file_to_check, {"linters": undesirable_functions_linter})

    @staticmethod
    def _get_used_libraries(file_text):
        """
        Create a set of all the libraries loaded in the provided R code.

        Libraries can be imported by 2 functions: library() and require()
        The library can either be the 1st argument (without an explicit keyword) or is specified out-of-order with the
        keyword 'package'.
        Library importing is found by a combination of regex and case splitting.
        There is no guarantee that returned library names refer to real (or even possibly valid) libraries.
        Args:
        file_text (str): R code as a multi-line string

        Returns:
            (list[tuple[int, str]]) Line numbers and library names from the text.
        """
        # NOTE:
        # This regex doesn't guarantee the R is valid (doesn't check quotes or brackets match)
        # R package naming standard don't allow brackets in package names, they will cause incorrect matches!!
        # R allows whitespace before function brackets
        # R has implicit line continuation inside brackets
        load_lib_exp = (
            r'(^|\s|;)'                 # Require a separator char to start so as not to match test_library, etc
            r'(library|require)\s*'     # Packages can be loaded by library or require.
            r'\((?P<body>.*?)\)'        # Matches function call part, validity of R not guaranteed.
        )

        # Match all the variants of package=...
        package_arg_pattern = re.compile(r'''\s*(\"package\"|\'package\'|package)\s*=''')

        def extract_lib_from_call(call_body: str):
            args = call_body.split(",")

            # First arg is package if there's no keyword
            if "=" not in args[0]:
                return args[0].strip('\'\"' + whitespace)

            # search for arg with key "package"
            for arg in args:
                if package_arg_pattern.match(arg):
                    return arg.split("=")[1].strip('\'\"' + whitespace)

            return ""  # No library found in call...

        return [
            (file_text.count("\n", 0, call.start() + 1) + 1, extract_lib_from_call(call["body"]))
            for call
            in re.finditer(load_lib_exp, file_text)
        ]

    @staticmethod
    def _check_restricted_libs(file, restricted_libraries):
        """
        Check whether any library from `restricted_libs` appears in `file`.

        Args:
            file (str): Path to the file to check
            restricted_libs (list[str]): Libraries which `file` is not permitted to use.

        Returns:
            (list[dict[str: (str | int)]]) An EDUKATE-compatible list of forbidden library occurrences
        """
        file = abspath(file)
        libs_used = Validator._get_used_libraries(Validator._read_file(file))

        failures = []
        for line, lib in libs_used:
            if lib in restricted_libraries:
                item = {
                    "type": "restricted library",
                    "info": f"library {lib} is not allowed in this file",
                    "file_path": file,
                    "line_number": line
                }
                failures.append(item)
        return failures

    @staticmethod
    def _check_restricted_functions(file, restricted_functions):
        """
        Check whether any function from `restricted_functions` appears in `file`.

        Args:
            file (str): Path to the file to check
            restricted_functions (list[str]): Functions which `file` is not permitted to use.

        Returns:
            (list[dict[str: (str | int)]]) An EDUKATE-compatible list of forbidden function invocations
        """
        function_usage = Validator._parse_lintr_output(
            Validator._invoke_lintr_restricted_functions(file, restricted_functions)
        )

        failures = []
        for fail in function_usage:
            fun_match = re.match(r"Function \"(?P<func>.+)\" is undesirable\.", fail['info'], re.M)
            if fun_match:
                item = {
                    "type": "restricted function",
                    "info": f"function {fun_match['func']} is not allowed in this file",
                    "file_path": file
                }

                failures.append(item)
        return failures

    @staticmethod
    def _invoke_error_lintr(file_to_check):
        """
        Invoking linter with just the object_usage_linter argument to get just the syntax errors.

        Args:
            file_to_check (str): the relative/absolute path to the file to check.

        Returns:
            (str) the output from the linter.
        """
        # TODO: Do we really think this is safe?!?!? There's a warning in the docs not to use on untrusted code
        return Validator._invoke_lintr(file_to_check, lint_options={"linters": "c(object_usage_linter)"})

    @staticmethod
    def _check_errors(file_to_check):
        """
        Parses error from static analysis to check for syntax errors.

        Args:
            file_to_check: Path to the file to check for errors

        Returns:
        (list[dict[str: (str | int)]]) An EDUKATE-compatible list of syntax errors from the linter.
        """
        out = []
        installed_libs = Validator._get_installed_libraries()
        libs_used = Validator._get_used_libraries(Validator._read_file(file_to_check))

        for line, lib in libs_used:
            if lib not in installed_libs:
                temp = {
                    "type": "unknown library",
                    "info": f"the library {lib} used in not known, perhaps there is spelling mistake",
                    "file_path": file_to_check,
                    "line_number": line
                }

                out.append(temp)

        errors_list = Validator._parse_lintr_output(Validator._invoke_error_lintr(file_to_check))
        for error in errors_list:
            # unused variables have level `warning` but we consider them style errors and ignore them here
            if re.match(r"local variable \'.*?\' assigned but may not be used", error["info"]):
                continue

            temp = {
                "type": "syntax",
                "info": error["info"],
                "file_path": file_to_check,
                "line_number": error["line_number"]
            }

            out.append(temp)

        return out

    @staticmethod
    def validate_file(file_to_validate, restricted_libraries, restricted_functions):
        """
        This function will validate a single file checking for errors (syntactic) and failures.

        If there are none then it assigns the file a success.

        Args:
        file_to_validate (str): the path to the file to validate.

        restricted_libraries (list[str]): libraries which must not appear in `file_to_validate`.
        restricted_functions (list[str]): functions whuch must not be invoked in `file_to_validate`.

        Returns:
            (tuple[dict[str: (str | int)], dict[str: (str | int)], dict[str: (str | int)]])
            The successes, failures, and errors in the file respectively.
            If a file has no errors then it gets the success of having no errors, etc.
        """
        successes = []

        lib_failures = Validator._check_restricted_libs(file_to_validate, restricted_libraries)
        if len(lib_failures) == 0:
            successes.append({
                "type": "restricted library",
                "info": "No restricted libraries used",
                "file_path": file_to_validate
            })

        fun_failures = Validator._check_restricted_functions(file_to_validate, restricted_functions)
        if len(fun_failures) == 0:
            successes.append({
                "type": "restricted function",
                "info": "No restricted functions used",
                "file_path": file_to_validate
            })

        errors = Validator._check_errors(file_to_validate)
        if len(errors) == 0:
            successes.append({
                "type": "syntax",
                "info": "No syntax errors found",
                "file_path": file_to_validate
            })

        return successes, lib_failures + fun_failures, errors

    @staticmethod
    def validate(config_yaml_file):
        """
        This function will decipher the requirements of the test and run validation test on each of the required files.

        :param config_file: a "config.yaml" file used to define which files to be tested and which
        funcitons/libraries are restricted.

        :return: returns a json with the keys passed & runners: {runner_key, errors, failures &
        successes} to be analysed by the existing software later on.
        """
        config = Validator._read_config(config_yaml_file)

        out = {
            "runners": [
                {
                    "successes": [],
                    "failures": [],
                    "errors":[],
                    "runner_key":"r:validate"
                }
            ],
            "passed": False
        }

        for file in config["files"]:
            file_path = joinpath(dirname(config_yaml_file), file)
            restricted_libraries = config["restricted_libraries"][file]
            restricted_functions = config["restricted_functions"][file]
            successes, failures, errors = Validator.validate_file(file_path, restricted_libraries, restricted_functions)
            out["runners"][0]["successes"].extend(successes)
            out["runners"][0]["failures"].extend(failures)
            out["runners"][0]["errors"].extend(errors)

        if (len(out["runners"][0]["errors"]) == 0 and len(out["runners"][0]["failures"]) == 0):
            out["passed"] = True

        return json.dumps(out, indent=2)
