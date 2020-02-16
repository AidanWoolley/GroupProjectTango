"""This class takes the static analysis from produces output in relevant format."""
import yaml
import re
import json
from os.path import abspath
from linter.Linter import Linter

__author__ = "Anish_Das_ad945"


class Validator(Linter):
    """The class uses the static analysis performed by Linter to produce required JSON."""

    @staticmethod
    def _read_config(config_yaml_file):
        """
        Parses the yaml file using the pyyaml library

        :param config_yaml_file: the relative path to the config.yaml file

        :return: dictionary containing the configuration.
        """
        with open(config_yaml_file, "r") as f:
            config = yaml.safe_load(f)

        return config

    @staticmethod
    def __read_file(file_to_validate):
        with open(file_to_validate, "r") as f:
            out = f.read()
        return out

    @staticmethod
    def _check_failures(file, restricted_libraries):
        """
        Checks for any failures in the code i.e. does it try to use any restricted librarires

        :param file: the file to check for restricted libraries

        :param restricted_libraries: the list of restricted libraries for the file

        :return: returns a list of dictionaries of the required format containing "type", "info"
        and "file_path".
        """

        file_path = abspath(file)
        file_text = Validator.__read_file(file)

        fail_line_regex = r"^library\((?P<lib>[A-Za-z]+)\)$"

        parsed_lines = re.finditer(fail_line_regex, file_text, re.M)

        restricted_libs_used = set()
        failures = []

        for line_match in parsed_lines:
            lib = line_match.group('lib')

            if lib in restricted_libraries:
                restricted_libs_used.add(lib)

        for lib in restricted_libs_used:
            item = {
                "type": "restricted library",
                "info": f"library {lib} is not allowed in this file",
                "file_path": file_path
            }
            failures.append(item)

        return failures

    @staticmethod
    def _check_errors(errors_list):
        """
        Parses error from static analysis to check for syntax errors

        :param errors_list: list of errors found by the static analysis tool

        :return: returns a list of dictionaries of the required type with "type", "info",
        "file_path", "details" & "line_number" as the keys.
        """

        out = []
        for error in errors_list:
            temp = {
                    "type": "Type of error (eg. syntax error)",
                    "info": "Error message (eg. invalid character)",
                    "file_path": "path to file",
                    "details": "Detailed error message",
                    "line_number": 0
                }

            if (error["type"] == "error" or
                    (error["type"] == "warning" and "no" == error["info"][:2])):

                temp["type"] = "syntax error"
                temp["info"] = error["info"]
                temp["file_path"] = error["file_path"]
                temp["line_number"] = error["line_number"]
                temp["details"] = ":".join([temp["file_path"],
                                            temp["line_number"],
                                            temp["type"],
                                            temp["info"]])

                out.append(temp)
        return out

    @staticmethod
    def validate_file(file_to_validate, linter_output, restricted_libraries):
        """
        This function will validate a single file checking for errors (syntactic) and failures.
        If there are none then it assigns the file a success.

        :param file_to_validate: the relative path to the file to validate

        :param linter_output: the output from the lintr package from R

        :param restricted_libraries: the list of restricted libraries for the file as deciphered
        from the config.yaml file

        :return: it returns a tuple containing the successes, failures, and errors in the file
        if a file has no errors then it gets the success of having no errors and if a file has no
        failures i.e. no restricted use then it gets another success item.
        """

        successes = []
        errors = []
        failures = []

        errors_list = Linter._errors_list_from_linter_output(file_to_validate, linter_output)
        errors = Validator._check_errors(errors_list)

        if len(errors) == 0:
            successes = [{
                "type": "syntax check succeeded",
                "info": "So far no errors found",
                "file_path": abspath(file_to_validate)
            }]

        failures = Validator._check_failures(file_to_validate, restricted_libraries)

        return successes, failures, errors

    @staticmethod
    def validate(config_file):
        """
        This function will decipher the requirements of the test and run validation test on each
        of the required files.

        :param config_file: a "config.yaml" file used to define which files to be tested and which
        funcitons/libraries are restricted

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

        for file in files:
            # remove the comment and remove what come after
            linter_output = Linter._invoke_lintr(file)
            # with open("linter_output.txt", "r") as f:
            #     linter_output = f.read()
            # # remove until here
            restricted_libraries = config["restricted_libraries"][file]
            args = [file, linter_output, restricted_libraries]
            successes, failures, errors = Validator.validate_file(*args)
            out["runners"][0]["successes"].extend(successes)
            out["runners"][0]["failures"].extend(failures)
            out["runners"][0]["errors"].extend(errors)

        if (len(out["runners"][0]["errors"]) == 0 and
            len(out["runners"][0]["failures"]) == 0):
            out["passed"] = True

        return json.dumps(out)
