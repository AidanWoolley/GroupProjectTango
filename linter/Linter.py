"""The class to perform static analysis of R code."""
import subprocess
import json
import xml.etree.ElementTree as xmlTree
from os import environ
from os.path import abspath
from pathlib import Path
__author__ = 'Kacper Walentynowicz'


class Linter:
    """The class to perform static analysis of R code."""

    @staticmethod
    def _score_file_by_errors(errors, ignore_multiple):
        """
        Given a list of errors, returns score displayed to the user being in range [0,1].

        The default scoring formula of deducting 0.05 per error.
        An enhancement is proposed in which ignore_multiple tells to ignore multiple occurrences of the same error -
        if f.ex "Only use double-quotes." error appears twice it is calculated only once in the final score.

        Args:
            errors: list of errors returned by the linter
            ignore_multiple (bool): whether to ignore multiple occurences of the same kind of error in calculating score
        Returns:
            Float: score of user's code
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

        command = [
            'Rscript',
            '-e',
            # checkstyle_output is XML which is easier to parse and guaranteed consistent
            # It must be written to a file, /proc/self/fd/1 is stdout!
            f'library("lintr"); checkstyle_output(lint("{object_to_lint}"), "/proc/self/fd/1")'
        ]
        # LANG=POSIX in env enforces only ascii characters
        return subprocess.run(command, stdout=subprocess.PIPE, env=dict(environ, LANG="POSIX")).stdout.decode("utf-8")

    @staticmethod
    def _errors_list_from_linter_output(linter_output):
        """
        Parses the multiline string `linter_output` and returns a list of errors.

        Returns:
            A list of dictionaries detailing errors in a format suitable for the EDUKATE platform
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
    def lint(object_to_lint, ignore_multiple_for_score=False):
        """
        The function to perform static analysis of R code.

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
            errors_list = Linter._errors_list_from_linter_output(lint_output)
            out["runners"][index]["errors"] = errors_list
            out["runners"][index]["score"] = Linter._score_file_by_errors(errors_list,
                                                                          ignore_multiple=ignore_multiple_for_score)
            out["runners"][index]["runner_key"] = "Hadley Wickham's R Style Guide"

        return json.dumps(out)
