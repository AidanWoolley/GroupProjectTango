"""This class takes the static analysis from produces output in relevant format."""
import yaml
import re
import json
from os.path import abspath
from pathlib import Path
from linter.Linter import Linter
import subprocess

__author__ = "Anish_Das_ad945"


class Validator():
    """The class uses the static analysis performed by Linter to produce required JSON."""

    @staticmethod
    def _read_config(config_yaml_file):
        """
        Parses the yaml file using the pyyaml library

        :param config_yaml_file: the relative path to the config.yaml file

        :return: dictionary containing the configuration.
        """
        file_path = abspath(config_yaml_file)

        if not Path(file_path).is_file():
            raise FileNotFoundError(config_yaml_file)

        with open(config_yaml_file, "r") as f:
            config = yaml.safe_load(f)

        return config

    @staticmethod
    def _get_libraries():
        """
        Runs an R script to return all the installed.packages() on the machine.

        :return: a list of all the available libraries that the user can use.
        """
        command = ["Rscript", abspath("get_libraries.R")]
        return subprocess.run(command, stdout=subprocess.PIPE).stdout.decode('utf-8')

    @staticmethod
    def __read_file(file_to_validate):
        with open(file_to_validate, "r") as f:
            out = f.read()
        return out

    @staticmethod
    def _invoke_lintr_failure(file_to_check, restricted_functions):
        """
        Specialized lintr call to only highlight the use of restricted functions

        :param file_to_check: the file to check use of any restricted functions in.

        :param restricted_functions: the list of restricted functions for this file now passed
        into the set of command line arguments

        :return: returns the output from invoking the file 'failure_linter.R' on file
        """

        file_to_check = abspath(file_to_check)

        if not Path(file_to_check).is_file():
            raise FileNotFoundError(file_to_check)

        command = ['Rscript', abspath('failure_linter.R'), file_to_check, *restricted_functions]
        return subprocess.run(command, stdout=subprocess.PIPE).stdout.decode('utf-8')

    @staticmethod
    def _get_used_libraries(file_text):
        """
        Goes through the file to extract quite basically the list of all the libraries that
        the file is using. It relies on regex to do so.

        :param file_text: The text of the file as in the string which is the file of R that we
        want to run.

        :return: A list of strings/libraries (that should be actual libraries) from the
        file_text.
        """
        file_text = file_text.split("\n")
        r1 = r"library\(\"(?P<lib>.+)\"\)"
        r2 = r"library\(\'(?P<lib>.+)\'\)"
        r3 = r"library\((?P<lib>.+)\)"

        libs_used = list()

        for i, line in enumerate(file_text):
            match = re.match(r1, line, re.M)
            if not match:
                match = re.match(r2, line, re.M)
            if not match:
                match = re.match(r3, line, re.M)

            if not match:
                continue

            lib = match.group('lib')
            if lib != lib.strip():
                lib = lib.strip().strip('\'').strip('\"')
            libs_used.append((lib, i))

        return libs_used

    @staticmethod
    def _check_failures(file, restricted_libraries, restricted_functions):
        """
        Checks for any failures in the code i.e. does it try to use any restricted librarires

        :param file: the file to check for restricted libraries

        :param restricted_libraries: the list of restricted libraries for the file

        :param restricted_functions: the list of restricted functions for the file

        :return: returns a list of dictionaries of the required format containing "type", "info"
        and "file_path".
        """



        # parsed_lines = re.finditer(r"^library\(?[\"|\'](?P<lib>.+)?[\"|\']\)$", file_text, re.M)

        file_text = Validator.__read_file(file)
        libs_used = Validator._get_used_libraries(file_text)

        failures = []
        restricted_libs_used = set()

        for lib, _ in libs_used:
            if lib in restricted_libraries:
                restricted_libs_used.add(lib)

        for lib in restricted_libs_used:
            item = {
                "type": "restricted library",
                "info": f"library {lib} is not allowed in this file",
                "file_path": abspath(file)
            }
            failures.append(item)

        if len(restricted_functions) == 0: return failures

        linter_output = Validator._invoke_lintr_failure(file, restricted_functions)

        function_usage = Linter._errors_list_from_linter_output(file, linter_output)

        for fail in function_usage:
            func_match = re.match(r"Function \"(?P<func>.+)\" is undesirable\.",
                                  fail['info'], re.M)
            if func_match:
                item = {
                    "type": "restricted function",
                    "info": f"function {func_match.group('func')} is not allowed in this file",
                    "file_path": abspath(file)
                }

                failures.append(item)

        return failures

    @staticmethod
    def _invoke_lintr_error(file_to_check):
        """
        Invoking linter with just the object_usage_linter argument to get just the syntax
        errors.

        :param file_to_check: the relative/absolute path to the file to check.

        :return: the output from the linter.
        """
        file_to_check = abspath(file_to_check)
        if not Path(file_to_check).is_file():
            raise FileNotFoundError(file_to_check)

        command = ['Rscript', abspath('error_linter.R'), file_to_check]
        return subprocess.run(command, stdout=subprocess.PIPE).stdout.decode("utf-8")

    @staticmethod
    def _check_errors(file, errors_list, libraries):
        """
        Parses error from static analysis to check for syntax errors.

        :param errors_list: list of errors found by the static analysis tool.

        :param libraries: the list of available libraries in the form of a string list.

        :return: returns a list of dictionaries of the required type with "type", "info",
        "file_path", "details" & "line_number" as the keys.
        """

        out = []

        file_text = Validator.__read_file(file)
        libs_used = Validator._get_used_libraries(file_text)

        for lib, i in libs_used:
            if lib in libraries:
                continue

            temp = {
                "type": "unknown library",
                "info": f"the library {lib} used in not known, perhaps there is spelling mistake",
                "file_path": abspath(file),
                "line_number": str(i+1),
            }
            temp["details"] = ": ".join([
                temp["file_path"],
                temp["line_number"],
                temp["type"],
                temp["info"]
            ])

            out.append(temp)

        for error in errors_list:

            if re.match(r"local variable \'.*\' assigned but may not be used",
                        error["info"],
                        re.M):
                continue

            temp = {
                "type": "syntax error",
                "info": error["info"],
                "file_path": error["file_path"],
                "line_number": error["line_number"]
            }
            temp["details"] = ": ".join([temp["file_path"],
                                        temp["line_number"],
                                        temp["type"],
                                        temp["info"]])

            out.append(temp)

        return out

    @staticmethod
    def validate_file(file_to_validate, restricted_libraries, libraries, restricted_functions):
        """
        This function will validate a single file checking for errors (syntactic) and failures.
        If there are none then it assigns the file a success.

        :param file_to_validate: the relative path to the file to validate.

        :param restricted_libraries: the list of restricted libraries for the file as deciphered
        from the config.yaml file.

        :param libraries: the list of available libraries in the form of a string list.

        :param restricted_functions: the list of restricted functions for the file as deciphered
        from the config.yaml file.

        :return: it returns a tuple containing the successes, failures, and errors in the file
        if a file has no errors then it gets the success of having no errors and if a file has no
        failures i.e. no restricted use then it gets another success item.
        """

        linter_output = Validator._invoke_lintr_error(file_to_validate)

        successes = []

        errors_list = Linter._errors_list_from_linter_output(file_to_validate, linter_output)
        errors = Validator._check_errors(file_to_validate, errors_list, libraries)

        if len(errors) == 0:
            successes = [{
                "type": "syntax check succeeded",
                "info": "So far no errors found",
                "file_path": abspath(file_to_validate)
            }]

        failures = Validator._check_failures(file_to_validate,
                                             restricted_libraries,
                                             restricted_functions)

        if len(failures) == 0:
            successes.append({
                "type": "no restricted library or function used",
                "info": "So far no restricted library/function used",
                "file_path": abspath(file_to_validate)
            })

        return successes, failures, errors

    @staticmethod
    def validate(config_file):
        """
        This function will decipher the requirements of the test and run validation test on each
        of the required files.

        :param config_file: a "config.yaml" file used to define which files to be tested and which
        funcitons/libraries are restricted.

        :return: returns a json with the keys passed & runners: {runner_key, errors, failures &
        successes} to be analysed by the existing software later on.
        """
        config = Validator._read_config(config_file)
        files = config["files"]

        out = {
            "runners": [
                {
                    "successes":[],
                    "failures":[],
                    "errors":[],
                    "runner_key":"r:validate"
                }
            ],
            "passed": False
        }

        libraries = Validator._get_libraries()
        libraries = libraries[5:-3]
        libraries = libraries.split(",")

        for file in files:
            restricted_libraries = config["restricted_libraries"][file]
            restricted_functions = config["restricted_functions"][file]
            args = [file, restricted_libraries, libraries,  restricted_functions]
            successes, failures, errors = Validator.validate_file(*args)
            out["runners"][0]["successes"].extend(successes)
            out["runners"][0]["failures"].extend(failures)
            out["runners"][0]["errors"].extend(errors)

        if (len(out["runners"][0]["errors"]) == 0 and
            len(out["runners"][0]["failures"]) == 0):
            out["passed"] = True

        return json.dumps(out, indent=2)
