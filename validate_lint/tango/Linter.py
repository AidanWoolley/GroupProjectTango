"""The class to perform static analysis of R code."""
import json
import subprocess
import xml.etree.ElementTree as xmlTree

from os import environ
from os.path import isfile, join as joinpath, dirname as dirname

import yaml
__author__ = 'Kacper Walentynowicz'


class Linter:
    """The class to perform static analysis of R code."""

    @staticmethod
    def _read_file(file):
        """
        Read a text file to a string.

        Args:
            file (str): Path to the file to read.

        Returns:
            (str): The contents of the file as a string.
        """
        with open(file, "r") as f:
            out = f.read()
        return out

    @staticmethod
    def _read_config(config_yaml_file):
        """
        Parses the yaml file using the pyyaml library.

        Args:
            config_yaml_file (str): the path to the config.yaml file

        Returns:
            (dict[str: Any]): dictionary containing the configuration.
        """
        return yaml.safe_load(Linter._read_file(config_yaml_file))

    @staticmethod
    def _score_file_by_errors(errors, ignore_multiple):
        """
        Given a list of errors, returns score displayed to the user being in range [0,1].

        The default scoring formula of deducting 0.05 per error.
        An enhancement is proposed in which ignore_multiple tells to ignore multiple occurrences of the same error -
        if f.ex "Only use double-quotes." error appears twice it is calculated only once in the final score.

        Args:
            errors (list[str]): list of errors returned by the linter
            ignore_multiple (bool): whether to ignore multiple occurences of the same kind of error in calculating score

        Returns:
            (float): score of user's code
        """
        if not ignore_multiple:
            return max(0, 1.0 - len(errors) * 0.05)

        found_style_errors = set()
        score = 1.0
        for error in errors:
            if error["type"] == 'info':
                if not error["info"] in found_style_errors:
                    score -= 0.05
                    found_style_errors.add(error["info"])

        return max(0, score)

    @staticmethod
    def _invoke_R(r_cmd):
        """
        Invoke Rscript to execute the R command provided.

        The command can be many commands, separatedby semicolons.
        The command is executed with LANG=POSIX to ensure only ascii characters.

        Args:
            r_cmd (str): The R command to execute.

        Returns:
            (str): The output of the command decoded with utf-8.
        """
        command = ["Rscript", "-e", r_cmd]
        # LANG=POSIX in env enforces only ascii characters
        return subprocess.run(command, stdout=subprocess.PIPE, env=dict(environ, LANG="POSIX")).stdout.decode("utf-8")

    @staticmethod
    def _invoke_lintr(file_to_lint, lint_options=None):
        """
        Invoke the R lintr on `file_to_lint`.

        Args:
            file_to_lint (str): Path to the file to lint

        Returns:
            (str): linter output of the R linter in checkstyle XML
        """
        if not isfile(file_to_lint):
            raise FileNotFoundError(file_to_lint)

        # If any options are provided, format them as opt1=val1, opt2=val2 with a prepended ', ' for the filename.
        options_str = (', ' + ', '.join([f'{k}={v}' for k, v in lint_options.items()])) if lint_options else ''

        # checkstyle_output is XML which is easier to parse and guaranteed consistent
        # It must be written to a file, /proc/self/fd/1 is stdout!
        r_cmd = f'library("lintr"); checkstyle_output(lint("{file_to_lint}"{options_str}), "/proc/self/fd/1")'
        return Linter._invoke_R(r_cmd)

    @staticmethod
    def _parse_lintr_output(linter_output):
        """
        Parses the multiline string `linter_output` and returns a list of errors.

        Args:
            linter_output (str): The checkstyle XML output from lintr.

        Returns:
            (list[dict[str: (str | int)]]): Errors in a format suitable for the EDUKATE platform.
        """
        lintr_xml = xmlTree.fromstring(linter_output)
        try:
            linted_file = lintr_xml[0].attrib["name"]
        except IndexError:
            return []  # No first child (which is node representing file) means no errors

        def create_err_dict(error):
            ret = {}
            ret["file_path"] = linted_file
            ret["line_number"] = error["line"]
            ret["type"] = error["severity"]
            ret["info"] = error["message"]
            ret["column_number"] = error["column"]
            return ret

        errors_list = [create_err_dict(error.attrib) for error in lintr_xml[0]]

        return errors_list

    @staticmethod
    def lint(config_yaml_file, ignore_multiple_for_score=False):
        """
        The function to perform static analysis of R code.

        Lints an object giving error, warning and style comments.
        Uses a separate R script to make use of 'lintr' library from that language.

        Invokes that script to produce output in stdout captured by subprocess,
        and parses that output to produce comments in the right format.

        Args:
            config_yamk_file: (str): Path to the config yaml detailing which files to lint.

        Returns:
            JSON object: a JSON describing errors in format suitable for EDUKATE platform
            Example given by the clients:
            {
                "runners": [
                    {
                        "errors": [
                            {
                                "file_path": "path to file",
                                "line_number": 0,
                                "type": "type of error (eg. bad spacing etc.)",
                                "info": "error message"
                            }
                        ],
                        "score": 0.95,
                        "runner_key": "quality checker name (eg. pep8, pylint, checkstyle, etc.)"
                    }
                ]
            }
        """
        files_to_lint = [
            joinpath(dirname(config_yaml_file), file)
            for file
            in Linter._read_config(config_yaml_file)["files"]
        ]
        errors_list = []
        for file_to_lint in files_to_lint:
            errors_list += Linter._parse_lintr_output(Linter._invoke_lintr(file_to_lint))

        score = Linter._score_file_by_errors(errors_list, ignore_multiple=ignore_multiple_for_score)
        out = {"runners": [{}]}
        out["runners"][0]["errors"] = errors_list
        out["runners"][0]["score"] = score
        out["runners"][0]["runner_key"] = "Hadley Wickham's R Style Guide"
        return json.dumps(out)
