import os
import subprocess
import json
from pathlib import Path
__author__ = 'Kacper Walentynowicz'
class Linter:
    '''
    The class to perform static analysis of R code.
    '''
    _LINTER_OUTPUT = '__linter_output__.txt'
    def __init__(self):
        pass

    @staticmethod
    def _score_formula(errors):
        '''
        Given a list of errors, returns score displayed to the user being in range [0,1]
        Currently the default scoring formula of reducing 0.05 per error.
        Args:
            errors: list of errors returned by the linter

        Returns:
            Float: score of user's code
        '''
        return max(0, 1.0 - len(errors) * 0.05)

    @staticmethod
    def _invoke_rscript(filename):
        '''
        Invokes the R script for the given file.
        Args:
            filename:

        Returns:
            None:
        '''
        my_file = Path(filename)
        if not my_file.is_file():
            raise FileNotFoundError
        else:
            command = './linter/lint_rfile.R ' + filename
            subprocess.call(command, shell=True)

    @staticmethod
    def _linter_output_line_to_error_dictionary(line):
        '''
        Name self-explanatory, so I will describe the algorithm used for parsing.
        The format of the line:
        FILEPATH:LINE_NUMBER:COLUMN_NUMBER:TYPE:MESSAGE
        like this one:
        /GroupProject/intro.r:2:1: style: Use spaces to indent, not tabs.

        Algorithm used for parsing:
        First, observe that the content is displayed by colons.
        Therefore, we start by splitting with ':', then stripping from trailing and leading spaces.
        The problem is that both FILEPATH and MESSAGE can contain ':' characters, so instead we parse from the middle.

        The algorithm searches for strings matching TYPE after split: {'error', 'warning', 'style'}.
        Then, what follows immediately before is a COLUMN_NUMBER, before - LINE_NUMBER and even more before -
        FILEPATH (possibly we need to join a few strings to obtain FILEPATH)
        MESSAGE is a concatenation of strings after the one responsible for TYPE.

        To check sanity of the algorithm, a flag is used to verify that there is exactly one place where TYPE could match.
        Violation of this raises RuntimeError.
        Args:
            line (str): meaningful line of _LINTER_OUTPUT used

        Returns:
            dictionary: error in format suitable for EDUKATE platform
        '''
        dict = {"file_path": "path to file", "line_number": 0, "type": "type of error", "info": "error message"}
        data = line.split(':')
        data = [x.strip() for x in data]
        path = ''
        message_type = ''
        message = ''
        line_number = 0
        column_number = 0

        flag = False
        for index in range(len(data)):
            if (data[index] == 'style' or data[index] == 'error' or data[index] == 'warning'):
                if flag:
                    raise RuntimeError('Two different message types in output line: ' + line)
                else:
                    flag = True

                message_type = data[index]
                column_number = int(data[index - 1])
                line_number = int(data[index - 2])
                for concat_path_iter in range(index - 2):
                    path += data[concat_path_iter]
                for concat_msg_iter in range(index + 1, len(data)):
                    message += data[concat_msg_iter]

        if not flag:
            raise RuntimeError('No message type in output line: ' + line)

        dict["file_path"] = path
        dict["line_number"] = line_number
        dict["type"] = message_type
        dict["info"] = message
        dict["column_number"] = column_number
        return dict

    @staticmethod
    def _errors_list_from_linter_output():
        '''
        Parses file _LINTER_OUTPUT and returns a list of errors.
        Uses the fact that each error is displayed in exactly three lines.
        Returns:

        '''
        errors = []
        with open(Linter._LINTER_OUTPUT) as linted_file:
            content = linted_file.readlines()
            for line in range(len(content)):
                if line % 3 == 0:
                    #every error description is three lines but only the first one is interesting for us
                    errors.append(Linter._linter_output_line_to_error_dictionary(content[line]))

        return errors

    @staticmethod
    def _clear_linter_output():
        '''
        Clearing after the script.
        Returns:
            None
        '''
        os.remove(Linter._LINTER_OUTPUT)

    @staticmethod
    def _parse_linter_output(keep_output):
        '''

        Args:
            keep_output (bool): whether to keep the lint in plaintext (_LINTER_OUTPUT)
        Returns:
            JSON object: a JSON describing errors in format suitable for EDUKATE platform
        '''
        out = {"runners": [
            {"errors": [],"score": 1,"runner_key": "Hadley Wickham's R Style Guide"}
        ]}

        errors_list = Linter._errors_list_from_linter_output()
        out["runners"][0]["errors"] = errors_list
        out["runners"][0]["score"] = Linter._score_formula(errors_list)

        if not keep_output:
            Linter._clear_linter_output()

        return json.dumps(out)

    @staticmethod
    def lint(filename, keep_output = False):
        '''
        Uses a separate R script to make use of 'lintr' library from that language.
        Invokes that script to produce temporary _LINTER_OUTPUT,
        parses that output to produce comments in the right format,
        and cleans _LINTER_OUTPUT if desired.
        Args:
            filename: path to file to produce analysis for.
            keep_output (bool): whether to keep the lint in plaintext (_LINTER_OUTPUT)

        Returns:
            JSON object: a JSON describing errors in format suitable for EDUKATE platform
        '''
        Linter._invoke_rscript(filename)
        return Linter._parse_linter_output(keep_output)

print(Linter.lint(filename='linter/example_linter_input.R', keep_output=False))
quit()