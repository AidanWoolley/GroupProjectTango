import unittest
import json
from os.path import abspath
from pathlib import Path
from Validation import Validator
import pytest

PATH = "test_validation/"


def __read_file(file):
    file_path = abspath(file)
    if not Path(file_path).is_file():
        raise FileNotFoundError(file)

    with open(file) as f:
        text = f.read()

    return text


def list_equal(list1, list2):
    list1.sort()
    list2.sort()
    assert list1 == list2


def test_exceptions():
    try:
        Validator._read_config('not_config.yaml')
        assert False
    except FileNotFoundError:
        assert True

    try:
        Validator.validate(PATH + 'no_r_config.yaml')
        assert False
    except FileNotFoundError:
        assert True


def test_read_config():
    config_yaml = 'test_validation/config.yaml'
    config = Validator._read_config(config_yaml)

    expected_config = dict(files=['file1.R', 'file2.R'],
                           restricted_libraries={
                               'file1.R': ['lib1', 'lib2', 'lib3'],
                               'file2.R': ['lib4', 'lib5', 'lib6']
                           },
                           restricted_functions={
                               'file1.R': ['func1', 'func2', 'func3'],
                               'file2.R': ['func0', 'func1', 'func2']
                           })

    # assert config, expected_config)
    assert config == expected_config


def test_get_used_libraries():
    known_libraries_output = Validator._get_used_libraries(
        __read_file(PATH + 'known_libraries.R'))
    restricted_functions_output = Validator._get_used_libraries(
        __read_file(PATH + 'restricted_functions.R'))
    restricted_libraries_output = Validator._get_used_libraries(
        __read_file(PATH + 'restricted_libraries.R'))
    success_output = Validator._get_used_libraries(
        __read_file(PATH + 'success.R'))
    syntax_error_output = Validator._get_used_libraries(
        __read_file(PATH + 'syntax_error.R'))
    unknown_libraries_output = Validator._get_used_libraries(
        __read_file(PATH + 'unknown_libraries.R'))

    known_libraries = [('askpass', 0),
                       ('assertthat', 1),
                       ('jsonlite', 2),
                       ('pkgbuild', 3),
                       ('pkgload', 4),
                       ('sys', 5),
                       ('testthat', 6),
                       ('base', 7),
                       ('boot', 8),
                       ('class', 9),
                       ('codetools', 10),
                       ('compiler', 11),
                       ('datasets', 12),
                       ('foreign', 13),
                       ('graphics', 14),
                       ('grDevices', 15),
                       ('grid', 16),
                       ('tcltk', 17),
                       ('tools', 18),
                       ('utils', 19)]

    restricted_functions = []
    restricted_libraries = [('restricted_library', 0), ('restricted_library', 1)]
    success = [('utils', 0)]
    syntax_error = []
    unknown_libraries = [('desC', 0), ('pkgload', 1), ('doesnt_exist', 2), ('util', 3)]

    known_libraries_output.sort()
    known_libraries.sort()
    assert known_libraries_output == known_libraries

    restricted_libraries_output.sort()
    restricted_libraries.sort()
    assert restricted_libraries_output == restricted_libraries

    assert restricted_functions_output == restricted_functions

    assert syntax_error_output == syntax_error

    assert success_output == success

    unknown_libraries_output.sort()
    unknown_libraries.sort()
    assert unknown_libraries_output == unknown_libraries


def test_failure_with_restricted_functions():
    output = Validator.validate_file(PATH + 'restricted_functions.R',
                                     [], [], ['print'])
    assert len(output) == 3
    success, failures, errors = output

    assert len(success) == 1

    success = success[0]
    assert success['type'] == 'syntax check succeeded'

    assert len(errors) == 0

    assert len(failures) == 1
    failures = failures[0]

    assert failures['type'] =='restricted function'
    assert failures['info'] == 'function print is not allowed in this file'


def test_failures_with_restricted_libraries():
    output = Validator.validate_file(PATH + 'restricted_libraries.R',
                                     ['restricted_library'],
                                     ['restricted_library'],
                                     [])

    assert len(output) == 3
    success, failures, errors = output

    assert len(success) == 1
    assert len(failures) == 1
    assert len(errors) == 0

    success = success[0]
    assert 'type' in success.keys()
    assert success['type'] == 'syntax check succeeded'

    failures = failures[0]
    assert 'type' in failures.keys()
    assert failures['type'] == 'restricted library'
    assert 'info' in failures.keys()
    assert failures['info'] == 'library restricted_library is not allowed in this file'


def test_errors_with_syntax_error():
    output = Validator.validate_file(PATH + 'syntax_error.R',
                                     [],
                                     [],
                                     [])
    assert len(output) == 3
    success, failures, errors = output

    assert len(success) == 1
    assert len(failures) == 0
    assert len(errors) == 3

    success = success[0]

    assert 'type' in success.keys()
    assert success['type'] == 'no restricted library or function used'

    for error in errors:
        list_equal(list(error.keys()),
                             ['type', 'info', 'file_path', 'line_number', 'details'])

        assert error['type']=='syntax error'

    assert errors[0]['info']=='no visible binding for global variable \'oen\'\r'
    assert errors[1]['info']=='no visible global function definition for \'five\'\r'
    assert errors[2]['info']=='unexpected \'{\'\r'

    assert errors[0]['line_number'] == '3'
    assert errors[1]['line_number'] == '6'
    assert errors[2]['line_number'] == '9'


def test_errors_with_unknown_libraries():
    output = Validator.validate_file(PATH + 'unknown_libraries.R',
                                     [],
                                     [],
                                     [])
    assert len(output) == 3
    success, failures, errors = output

    assert len(success) == 1
    assert len(failures) == 0
    assert len(errors) == 4

    success = success[0]

    assert 'type' in success.keys()
    assert success['type']=='no restricted library or function used'

    pkgs = ['desC', 'pkgload', 'doesnt_exist', 'util']
    for i, error in enumerate(errors):
        list_equal(list(error.keys()),
                             ['type', 'info', 'file_path', 'line_number', 'details'])
        assert error['type'] == "unknown library"
        assert error['line_number'] == str(i+1)
        lib = error['info'].split(' ')[2]
        assert pkgs[i] == lib


def test_success():
    output = json.loads(Validator.validate(PATH + 'success.yaml'))
    list_equal(list(output.keys()), ['runners', 'passed'])
    assert output['passed']

    runners = output['runners'][0]
    list_equal(list(runners.keys()),
                         ['successes', 'failures', 'errors', 'runner_key'])

    assert len(runners['failures']) == 0
    assert len(runners['errors']) == 0

    successes = runners['successes']
    for success in successes:
        list_equal(list(success.keys()), ['type', 'info', 'file_path'])
        assert (success['type'] == 'syntax check succeeded' or
                success['type'] == 'no restricted library or function used')
        assert (success['info'] == 'So far no errors found' or
                success['info'] == 'So far no restricted library/function used')