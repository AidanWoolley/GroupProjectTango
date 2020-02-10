"""The class to perform static analysis of R code."""
import os
import subprocess
import json
import re
from pathlib import Path
__author__ = 'Kacper Walentynowicz'


class Linter:
    """The class to perform static analysis of R code."""
    def __init__(self, file_to_lint):
        """The class to perform static analysis of R code."""
        self.file_to_lint = os.path.abspath(file_to_lint)

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

    def _invoke_lintr(self):
        """
        Invokes the R  linter script for `self.file_to_lint`.

        Args:
            None

        Returns:
            String linter output of the R linter.
        """
        if not Path(self.file_to_lint).is_file():
            raise FileNotFoundError(self.file_to_lint)

        command = ['Rscript', 'lint_rfile.R', self.file_to_lint]
        return subprocess.run(command, stdout=subprocess.PIPE).stdout.decode("utf-8")

    def _errors_list_from_linter_output(self, linter_output):
        """
        Parses the multiline string `linter_output` and returns a list of errors.

        Returns:
            A list of dictionaries detailing errors in a format suitable for the EDUKATE platform
        """
        err_line_regex = (
            rf"^(?P<path>{self.file_to_lint}):"
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

        return errors_list

    def lint(self):
        """
        Uses a separate R script to make use of 'lintr' library from that language.

        Invokes that script to produce output in stdout captured by subprocess,
        and parses that output to produce comments in the right format.

        Args:
            filename: path to file to produce analysis for.
            keep_output (bool): whether to keep the lint in plaintext (_LINTER_OUTPUT)

        Returns:
            JSON object: a JSON describing errors in format suitable for EDUKATE platform
        """
        lint_output = self._invoke_lintr()

        out = {"runners": [
            {"errors": [], "score": 1.0, "runner_key": "Hadley Wickham's R Style Guide"}
        ]}

        errors_list = self._errors_list_from_linter_output(lint_output)

        out["runners"][0]["errors"] = errors_list
        out["runners"][0]["score"] = Linter._score_file_by_errors(errors_list)

        return json.dumps(out)


if __name__ == '__main__':
    print(Linter("example_linter_input.R").lint())
