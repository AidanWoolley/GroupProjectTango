import yaml
import re
import json
from linter.Linter import Linter

__author__ = "Anish Das (ad945)"


class Validator:
    """The class uses the static analysis performed by Linter to produce required JSON"""

    @staticmethod
    def _read_config(config_yaml_file):
        """
        Parses the yaml file using the pyyaml library
        :param config_yaml_file: the relative path to the config.yaml file
        :return: dictionary containing the configuration
        """
        with open(config_yaml_file, "r") as f:
            config = yaml.safe_load(f)

        return config

    @staticmethod
    def _check_failures(config, errors_list):
        pass

    @staticmethod
    def _check_errors(errors_list):
        """
        Parses error from static analysis to check for syntax errors
        :param errors_list:
        :return:
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
    def validate(file_to_validate, config_file):
        out = {
            "runners": [
                {
                    "sucesses":[],
                    "failures":[],
                    "errors":[],
                    "runner_key":"r:validate"
                }
            ],
            "passed": False
        }

        errors_list = Linter.lint(file_to_validate)
        config = Validator._read_config(config_file)

        errors = Validator._check_errors(errors_list)
        if len(errors):
            out["runners"][0]["errors"] = errors

        # TODO: check for the failures

        # TODO: if there are no errors and failures update successes/passed

        return json.dump(out)
