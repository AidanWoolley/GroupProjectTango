# """Unit tests for Linter.py."""
# import json
# import os
# 
# from contextlib import contextmanager
# 
# import yaml
# 
# from ..tango.Linter import Linter
# 
# PATH_TO_TEST_RES = os.path.join(os.path.dirname(__file__), "linter_test_res")
# 
# 
# def _test_file(file):
#     """
#     Generate an absolute path to a test file from its name.
# 
#     Args:
#         file (str): the name of the test file.
# 
#     Returns:
#         (str) absolute path to `file`
#     """
#     return os.path.abspath(os.path.join(PATH_TO_TEST_RES, file))
# 
# 
# @contextmanager
# def _create_test_yaml(filename):
#     with open(_test_file(f"{filename}.yaml"), "w") as y:
#         yaml.dump({
#             "files": [f"{filename}.R"],
#             "restricted_functions": {f"{filename}.R": []},
#             "restricted_libraries": {f"{filename}.R": []}
#         }, y)
# 
#     yield _test_file(f"{filename}.yaml")
# 
#     os.remove(_test_file(f"{filename}.yaml"))
# 
# 
# def _ordered(obj):
#     """
#     Private helper function for checking equality of Python objects.
# 
#     Args:
#         obj: object
# 
#     Returns:
#         obj: ordered representation of object obj
#     """
#     if isinstance(obj, dict):
#         return sorted((k, _ordered(v)) for k, v in obj.items())
#     if isinstance(obj, list):
#         return sorted(_ordered(x) for x in obj)
#     else:
#         return obj
# 
# 
# def test_invoke_lintr():
#     """
#     Checks that lintr works on invocation.
# 
#     Returns:
#         None
#     """
#     basic_warning_path = _test_file("warning.R")
#     basic_warning_result = (
#         '<?xml version="1.0" encoding="UTF-8"?>\n<checkstyle version="lintr-2.0.1">\n  '
#         f'<file name="{basic_warning_path}">\n    '
#         '<error line="2" column="3" severity="warning" '
#         'message="local variable \'some_variable\' assigned but may not be used"/>\n  </file>\n</checkstyle>\n'
#     )
#     lintr_result = Linter._invoke_lintr(basic_warning_path)
#     assert lintr_result == basic_warning_result
# 
# 
# def test_linter_raises_error_if_filenotfound():
#     """
#     Checks that linter raises a proper error if file is not found.
# 
#     Returns:
#         None
#     """
#     try:
#         Linter.lint(_test_file("notfound.R"))
#         assert False
#     except FileNotFoundError:
#         assert True
# 
# 
# def test_linter_handles_files_with_special_characters():
#     """
#     Checks that linter handles difficult file paths.
# 
#     Returns:
#         None
#     """
#     desired_result = {"runners": [{"errors": [{
#         "file_path": _test_file("!@# $%^&*(h ello: world.R"),
#         "line_number": "1",
#         "type": "info",
#         "info": "Only use double-quotes.",
#         "column_number": "7"}], "score": 0.95, "runner_key": "Hadley Wickham's R Style Guide"}]}
#     with _create_test_yaml("!@# $%^&*(h ello: world") as f:
#         lint_result = json.loads(Linter.lint(f))
#     assert _ordered(lint_result) == _ordered(desired_result)
# 
# 
# def test_linter_includes_compile_errors():
#     """
#     Checks that linter includes compile errors.
# 
#     Returns:
#         None
#     """
#     desired_result = {"runners": [{"errors": [{
#         "file_path": _test_file("compilation_error.R"),
#         "line_number": "1",
#         "type": "error",
#         "info": "unexpected end of input",
#         "column_number": "20"}], "score": 0.95, "runner_key": "Hadley Wickham's R Style Guide"}]}
#     with _create_test_yaml("compilation_error") as f:
#         lint_result = json.loads(Linter.lint(f))
#     assert _ordered(lint_result) == _ordered(desired_result)
# 
# 
# def test_linter_includes_warnings():
#     """
#     Checks that linter includes code warnings.
# 
#     Returns:
#         None
#     """
#     desired_result = {"runners": [{"errors": [{
#         "file_path": _test_file("warning.R"),
#         "line_number": "2",
#         "type": "warning",
#         "info": "local variable 'some_variable' assigned but may not be used",
#         "column_number": "3"}], "score": 0.95, "runner_key": "Hadley Wickham's R Style Guide"}]}
#     with _create_test_yaml("warning") as f:
#         lint_result = json.loads(Linter.lint(f))
#     assert _ordered(lint_result) == _ordered(desired_result)
# 
# 
# def test_linter_returns_score_0_when_many_errors():
#     """
#     Checks that linter does not return negative scores.
# 
#     Returns:
#         None
#     """
#     with _create_test_yaml("zero") as f:
#         lint_result = Linter.lint(f)
#     dict_result = json.loads(lint_result)
#     assert dict_result["runners"][0]["score"] == 0
# 
# 
# def test_linter_on_perfect_code():
#     """
#     Checks that linter returns the correct output when there are no errors in the code.
# 
#     Returns:
#         None
#     """
#     desired_result = ({"runners": [{"errors": [], "score": 1, "runner_key": "Hadley Wickham's R Style Guide"}]})
#     with _create_test_yaml("perfect") as f:
#         lint_result = json.loads(Linter.lint(f))
#     assert _ordered(lint_result) == _ordered(desired_result)
# 
# 
# def test_linter_correctly_ignores_multiple_similar_style_errors():
#     """
#     Checks that linter correctly ignores multiple similar style errors when the feature is enabled.
# 
#     Returns:
#         None
#     """
#     with _create_test_yaml("zero") as f:
#         lint_result = Linter.lint(f, ignore_multiple_for_score=True)
#     dict_result = json.loads(lint_result)
#     assert dict_result["runners"][0]["score"] == 0.95
