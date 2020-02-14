"""
Unit tests for Linter.py.
"""
from linter.Linter import Linter
import os
import json
PATH_TO_FILES = os.getcwd() + "/linter/testprograms/"
print(PATH_TO_FILES)

def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj

def test_linter_raises_error_if_filenotfound():
    try:
        Linter.lint("linter/testprograms/notfound.R")
        assert False
    except FileNotFoundError:
        assert True


def test_linter_handles_files_with_special_characters():
    desired_result = {"runners": [{"errors": [{
        "file_path": PATH_TO_FILES + "!@# $%^&*(h ello: world.R",
        "line_number": "1",
        "type": "style",
        "info": "Only use double-quotes.",
        "column_number": "7"}], "score": 0.95, "runner_key": "Hadley Wickham's R Style Guide"}]}

    lint_result = json.loads(Linter.lint("linter/testprograms/!@# $%^&*(h ello: world.R"))
    assert ordered(lint_result) == ordered(desired_result)


def test_linter_includes_compile_errors():
    desired_result = {"runners": [{"errors": [{
        "file_path": PATH_TO_FILES + "compilation_error.R",
        "line_number": "1",
        "type": "error",
        "info": "unexpected end of input",
        "column_number": "20"}], "score": 0.95, "runner_key": "Hadley Wickham's R Style Guide"}]}

    lint_result = json.loads(Linter.lint("linter/testprograms/compilation_error.R"))
    assert ordered(lint_result) == ordered(desired_result)

def test_linter_includes_warnings():
    desired_result = {"runners": [{"errors": [{
        "file_path": PATH_TO_FILES + "warning.R",
        "line_number": "2",
        "type": "warning",
        "info": "local variable 'some_variable' assigned but may not be used",
        "column_number":"3"}], "score": 0.95, "runner_key": "Hadley Wickham's R Style Guide"}]}

    lint_result = json.loads(Linter.lint("linter/testprograms/warning.R"))
    assert ordered(lint_result) == ordered(desired_result)

def test_linter_returns_score_0_when_many_errors():
    lint_result = Linter.lint("linter/testprograms/zero.R")
    dict_result = json.loads(lint_result)
    assert dict_result["runners"][0]["score"] == 0

def test_linter_on_perfect_code():
    desired_result = ({"runners":
        [{"errors": [], "score": 1, "runner_key": "Hadley Wickham's R Style Guide"}]})

    lint_result = json.loads(Linter.lint("linter/testprograms/perfect.R"))
    assert ordered(lint_result) == ordered(desired_result)

test_linter_raises_error_if_filenotfound()
test_linter_handles_files_with_special_characters()
test_linter_includes_compile_errors()
test_linter_includes_warnings()
test_linter_returns_score_0_when_many_errors()
test_linter_on_perfect_code()

print("SUCCESS")