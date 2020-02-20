"""The class to perform static analysis of R code."""
import subprocess
import json
import re
from os.path import abspath
from pathlib import Path
__author__ = 'Kacper Walentynowicz'


class Linter:
    """The class to perform static analysis of R code."""

    @staticmethod
    def _score_file_by_errors(errors):
        """
        Given a list of errors, returns score displayed to the user being in range [0,1].

        Currently the default scoring formula of deducting 0.05 per error.

        Args:
            errors: list of errors returned by the linter

        Returns:
            Float: score of user's code
        """
        return max(0, 1.0 - len(errors) * 0.05)

    @staticmethod
    def _invoke_lintr(object_to_lint):
        """
        Invokes the R  linter script for `self.object_to_lint`.

        Args:
            None

        Returns:
            String linter output of the R linter.
        """
        object_to_lint = abspath(object_to_lint)
        if not Path(object_to_lint).is_file():
            raise FileNotFoundError(object_to_lint)

        command = ['Rscript', 'linter/lint_rfile.R', object_to_lint]
        return subprocess.run(command, stdout=subprocess.PIPE).stdout.decode("utf-8")

    @staticmethod
    def _errors_list_from_linter_output(linted_file, linter_output):
        """
        Parses the multiline string `linter_output` and returns a list of errors.

        Returns:
            A list of dictionaries detailing errors in a format suitable for the EDUKATE platform
        """
        linted_file = abspath(linted_file)
        err_line_regex = (
            rf"^(?P<path>{re.escape(linted_file)}):"
            r"(?P<line>\d+):"
            r"(?P<col>\d+): "
            r"(?P<type>style|warning|error): "
            r"(?P<msg>.*)$"
        )

        def create_err_dict(line_match):
            ret = {}
            ret["file_path"] = line_match.group('path')
            ret["line_number"] = line_match.group('line')
            ret["type"] = line_match.group('type')
            ret["info"] = line_match.group('msg')
            ret["column_number"] = line_match.group('col')
            return ret

        parsed_lines = re.finditer(err_line_regex, linter_output, re.M)
        errors_list = [create_err_dict(line) for line in parsed_lines]

        for error in errors_list:
            error["info"] = error["info"].replace("\u2018", "'").replace("\u2019", "'")

        return errors_list

    @staticmethod
    def lint(object_to_lint):
        """
        Lints an object giving error, warning and style comments.
        Uses a separate R script to make use of 'lintr' library from that language.

        Invokes that script to produce output in stdout captured by subprocess,
        and parses that output to produce comments in the right format.

        Args:
            object_to_lint: object to produce analysis for.
            A single file or a list of files is currently supported.

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
        if type(object_to_lint) is not list:
            object_to_lint = [object_to_lint]

        out = {"runners": []}
        for index in range(len(object_to_lint)):
            out["runners"].append({})
            lint_output = Linter._invoke_lintr(object_to_lint[index])
            errors_list = Linter._errors_list_from_linter_output(object_to_lint[index], lint_output)
            out["runners"][index]["errors"] = errors_list
            out["runners"][index]["score"] = Linter._score_file_by_errors(errors_list)
            out["runners"][index]["runner_key"] = "Hadley Wickham's R Style Guide"

        return json.dumps(out)
