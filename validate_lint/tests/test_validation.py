"""Tests for Validation.py."""
from contextlib import contextmanager
from os import remove
from os.path import abspath, dirname, join as joinpath

import yaml

from pytest import raises as assert_raises
from ..tango.validation import Validator

PATH_TO_TEST_RES = joinpath(dirname(__file__), "validation_test_res")


def _test_file(file):
    """
    Generate an absolute path to a test file from its name.

    Args:
        file (str): the name of the test file.

    Returns:
        (str) absolute path to `file`
    """
    return abspath(joinpath(PATH_TO_TEST_RES, file))


@contextmanager
def _create_test_yaml(filename):
    """
    Create and then remove a trivial test yaml for and arbitrary R file.

    Args:
        filename (str): filename, without extension, for which yaml will be created.

    Yields:
        (str): absolute path to the created yaml
    """
    with open(_test_file(f"{filename}.yaml"), "w") as y:
        yaml.dump({
            "files": [f"{filename}.R"],
            "restricted_functions": {f"{filename}.R": []},
            "restricted_libraries": {f"{filename}.R": []}
        }, y)

    yield _test_file(f"{filename}.yaml")

    remove(_test_file(f"{filename}.yaml"))


def _read_file(file):
    """
    Read `file` to a string.

    Args:
        file (str): the path to the file

    Returns:
        (str): The text of the file
    """
    with open(_test_file(file)) as f:
        text = f.read()

    return text


def test_exceptions():
    """Tests if the code properly throws exceptions when a file doesn't exist or not."""
    with assert_raises(FileNotFoundError):
        Validator._read_config('not_config.yaml')

    with assert_raises(FileNotFoundError):
        Validator.validate(_test_file('no_r_config.yaml'))


def test_read_config():
    """Tests to see if the config file is read properly."""
    config = Validator._read_config(_test_file("config.yaml"))

    expected_config = {
        "files": [
            'file1.R',
            'file2.R'
        ],
        "restricted_libraries": {
            'file1.R': [
                'lib1',
                'lib2',
                'lib3'
            ],
            'file2.R': [
                'lib4',
                'lib5',
                'lib6'
            ]
        },
        "restricted_functions": {
            'file1.R': [
                'func1',
                'func2',
                'func3'
            ],
            'file2.R': [
                'func0',
                'func1',
                'func2'
            ]
        }
    }

    assert config == expected_config


def test_get_used_libraries():
    """
    Test that the list of (line_number, used_library) tuples from the code match the expected values.

    They ought to be created in line order, so no need to sort the output.
    """
    # TODO Surely there's a nicer way to do this test...
    known_libraries_output = Validator._get_used_libraries(_read_file('known_libraries.R'))
    known_libraries = [
        (1, 'askpass'),
        (2, 'assertthat'),
        (3, 'jsonlite'),
        (4, 'pkgbuild'),
        (5, 'pkgload'),
        (6, 'sys'),
        (7, 'testthat'),
        (8, 'base'),
        (9, 'boot'),
        (10, 'class'),
        (11, 'codetools'),
        (12, 'compiler'),
        (13, 'datasets'),
        (14, 'foreign'),
        (15, 'graphics'),
        (16, 'grDevices'),
        (17, 'grid'),
        (18, 'tcltk'),
        (19, 'tools'),
        (20, 'utils')
    ]
    assert known_libraries_output == known_libraries

    restricted_libraries_output = Validator._get_used_libraries(_read_file('restricted_libraries.R'))
    restricted_libraries = [
        (1, 'rjson'),
        (2, 'rjson'),
        (3, 'rjson'),
        (4, 'other_lib'),
        (5, 'extra_lib')
    ]
    assert restricted_libraries_output == restricted_libraries

    unknown_libraries_output = Validator._get_used_libraries(_read_file('unknown_libraries.R'))
    unknown_libraries = [
        (1, 'desC'),
        (2, 'pkgloaddf'),
        (3, 'doesntexist'),
        (4, 'util')
    ]
    assert unknown_libraries_output == unknown_libraries

    # Should be empty / only 1 item so no need to sort
    success_output = Validator._get_used_libraries(_read_file('success.R'))
    assert success_output == [(1, 'utils')]

    restricted_functions_output = Validator._get_used_libraries(_read_file('restricted_functions.R'))
    assert restricted_functions_output == []

    syntax_error_output = Validator._get_used_libraries(_read_file('syntax_error.R'))
    assert syntax_error_output == []


def test_failure_with_restricted_functions():
    """Test to see if failures by using restricted functions is caught."""
    output = Validator.validate_file(_test_file('restricted_functions.R'), [], ['print'])
    assert len(output) == 3

    success, failures, errors = output

    assert len(success) == 2
    assert success[0]['type'] == 'restricted library'
    assert success[1]['type'] == 'syntax'

    assert len(errors) == 0

    assert len(failures) == 1
    assert failures[0]['type'] == 'restricted function'
    assert failures[0]['info'] == 'function print is not allowed in this file'


def test_failures_with_restricted_libraries():
    """Test to see if failures due to use of restricted libraries is caught."""
    output = Validator.validate_file(_test_file('restricted_libraries.R'), ['rjson'], [])
    assert len(output) == 3

    success, failures, errors = output

    assert len(failures) == 3

    assert len(errors) == 2

    assert len(success) == 1
    assert success[0]['type'] == 'restricted function'

    # Other entries will be same pattern
    assert failures[0]['type'] == 'restricted library'
    assert failures[0]['info'] == 'library rjson is not allowed in this file'


def test_errors_with_syntax_error():
    """Test to see if syntax errors are caught."""
    output = Validator.validate_file(_test_file('syntax_error.R'), [], [])
    assert len(output) == 3

    success, failures, errors = output

    assert len(success) == 2
    assert success[0]['type'] == 'restricted library'
    assert success[1]['type'] == 'restricted function'

    assert len(failures) == 0

    assert len(errors) == 3

    for error in errors:
        assert error.keys() == {'type', 'info', 'file_path', 'line_number'}

    assert errors[0]['type'] == 'unknown variable'
    assert errors[0]['info'] == 'no visible binding for global variable \'oen\''
    assert errors[0]['line_number'] == 3

    assert errors[1]['type'] == 'unknown function'
    assert errors[1]['info'] == 'no visible global function definition for \'five\''
    assert errors[1]['line_number'] == 6

    assert errors[2]['type'] == 'syntax'
    assert errors[2]['info'] == 'unexpected \'{\''
    assert errors[2]['line_number'] == 9


def test_errors_with_unknown_libraries():
    """Test to see if use of unkown libraries is caught."""
    output = Validator.validate_file(_test_file("unknown_libraries.R"), [], [])
    assert len(output) == 3

    success, failures, errors = output

    assert len(failures) == 0

    assert len(success) == 2
    assert success[0]['type'] == 'restricted library'
    assert success[1]['type'] == 'restricted function'

    pkgs = [None, 'desC', 'pkgloaddf', 'doesntexist', 'util']
    assert len(errors) == 4
    for i, error in enumerate(errors, start=1):
        assert error.keys() == {'type', 'info', 'file_path', 'line_number'}
        assert error['type'] == "unknown library"
        assert error['line_number'] == i
        assert pkgs[i] == error['info'].split(' ')[2]  # Extract lib name from error message


def test_success():
    """Test to see if proper code passes the validator."""
    output = Validator.validate(_test_file('success.yaml'))
    assert output.keys() == {'runners', 'passed'}
    assert output['passed']

    runner = output['runners'][0]
    assert runner.keys() == {'successes', 'failures', 'errors', 'runner_key'}

    assert len(runner['failures']) == 0
    assert len(runner['errors']) == 0

    successes = runner['successes']
    assert successes[0]["type"] == "restricted library"
    assert successes[0]["info"] == "No restricted libraries used"
    assert successes[1]["type"] == "restricted function"
    assert successes[1]["info"] == "No restricted functions used"
    assert successes[2]["type"] == "syntax"
    assert successes[2]["info"] == "No syntax errors found"
