import unittest
import json
from os.path import abspath
from pathlib import Path
from validation.Validation import Validator


class TestValidator(unittest.TestCase):

    @staticmethod
    def __read_file(file):
        file_path = abspath(file)
        if not Path(file_path).is_file():
            raise FileNotFoundError(file)

        with open(file) as f:
            text = f.read()

        return text

    def test_exceptions(self):
        self.assertRaises(FileNotFoundError, Validator._read_config, 'not_config.yaml')

        self.assertRaises(FileNotFoundError, Validator.validate, 'no_r_config.yaml')

    def test_read_config(self):
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

        self.assertEqual(config, expected_config)

    def test_get_used_libraries(self):
        known_libraries_output = Validator._get_used_libraries(
            TestValidator.__read_file('test_validation/known_libraries.R'))
        restricted_functions_output = Validator._get_used_libraries(
            TestValidator.__read_file('test_validation/restricted_functions.R'))
        restricted_libraries_output = Validator._get_used_libraries(
            TestValidator.__read_file('test_validation/restricted_libraries.R'))
        success_output = Validator._get_used_libraries(
            TestValidator.__read_file('test_validation/success.R'))
        syntax_error_output = Validator._get_used_libraries(
            TestValidator.__read_file('test_validation/syntax_error.R'))
        unknown_libraries_output = Validator._get_used_libraries(
            TestValidator.__read_file('test_validation/unknown_libraries.R'))

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

        self.assertListEqual(known_libraries, known_libraries_output)
        self.assertListEqual(restricted_functions, restricted_functions_output)
        self.assertListEqual(restricted_libraries, restricted_libraries_output)
        self.assertListEqual(success, success_output)
        self.assertListEqual(syntax_error, syntax_error_output)
        self.assertListEqual(unknown_libraries, unknown_libraries_output)

    def test_failure_with_restricted_functions(self):
        output = Validator.validate_file('test_validation/restricted_functions.R',
                                         [], [], ['print'])
        self.assertTrue(len(output) == 3)
        success, failures, errors = output

        self.assertTrue(len(success) == 1)

        success = success[0]
        self.assertEqual(success['type'], 'syntax check succeeded')

        self.assertTrue(len(errors) == 0)

        self.assertTrue(len(failures) == 1)
        failures = failures[0]

        self.assertEqual(failures['type'], 'restricted function')
        self.assertEqual(failures['info'], 'function print is not allowed in this file')

    def test_failures_with_restricted_libraries(self):
        output = Validator.validate_file('test_validation/restricted_libraries.R',
                                         ['restricted_library'],
                                         ['restricted_library'],
                                         [])

        self.assertTrue(len(output) == 3)
        success, failures, errors = output

        self.assertTrue(len(success) == 1)
        self.assertTrue(len(failures) == 1)
        self.assertTrue(len(errors) == 0)

        success = success[0]
        self.assertTrue('type' in success.keys())
        self.assertEqual(success['type'], 'syntax check succeeded')

        failures = failures[0]
        self.assertTrue('type' in failures.keys())
        self.assertEqual(failures['type'], 'restricted library')
        self.assertTrue('info' in failures.keys())
        self.assertEqual(failures['info'],
                         'library restricted_library is not allowed in this file')

    def test_errors_with_syntax_error(self):
        output = Validator.validate_file('test_validation/syntax_error.R',
                                         [],
                                         [],
                                         [])
        self.assertTrue(len(output) == 3)
        success, failures, errors = output

        self.assertTrue(len(success) == 1)
        self.assertTrue(len(failures) == 0)
        self.assertTrue(len(errors) == 3)

        success = success[0]

        self.assertTrue('type' in success.keys())
        self.assertEqual(success['type'],
                         'no restricted library or function used')

        for error in errors:
            self.assertListEqual(list(error.keys()),
                             ['type', 'info', 'file_path', 'line_number', 'details'])

            self.assertEqual(error['type'], 'syntax error')

        self.assertEqual(errors[0]['info'],
                         'no visible binding for global variable \'oen\'\r')
        self.assertEqual(errors[1]['info'],
                         'no visible global function definition for \'five\'\r')
        self.assertEqual(errors[2]['info'],
                         'unexpected \'{\'\r')

        self.assertEqual(errors[0]['line_number'], '3')
        self.assertEqual(errors[1]['line_number'], '6')
        self.assertEqual(errors[2]['line_number'], '9')

    def test_errors_with_unknown_libraries(self):
        output = Validator.validate_file('test_validation/unknown_libraries.R',
                                         [],
                                         [],
                                         [])
        self.assertTrue(len(output) == 3)
        success, failures, errors = output

        self.assertTrue(len(success) == 1)
        self.assertTrue(len(failures) == 0)
        self.assertTrue(len(errors) == 4)

        success = success[0]

        self.assertTrue('type' in success.keys())
        self.assertEqual(success['type'],
                         'no restricted library or function used')

        pkgs = ['desC', 'pkgload', 'doesnt_exist', 'util']
        for i, error in enumerate(errors):
            self.assertListEqual(list(error.keys()),
                                 ['type', 'info', 'file_path', 'line_number', 'details'])
            self.assertEqual('unknown library', error['type'])
            self.assertEqual(str(i+1), error['line_number'])
            lib = error['info'].split(' ')[2]
            self.assertEqual(pkgs[i], lib)

    def test_success(self):
        output = json.loads(Validator.validate('test_validation/success.yaml'))

        self.assertListEqual(list(output.keys()), ['runners', 'passed'])
        self.assertTrue(output['passed'])

        runners = output['runners'][0]
        self.assertListEqual(list(runners.keys()),
                             ['successes', 'failures', 'errors', 'runner_key'])

        self.assertTrue(len(runners['failures']) == 0)
        self.assertTrue(len(runners['errors']) == 0)

        successes = runners['successes']
        for success in successes:
            self.assertListEqual(list(success.keys()), ['type', 'info', 'file_path'])
            self.assertTrue(success['type'] == 'syntax check succeeded' or
                            success['type'] == 'no restricted library or function used')
            self.assertTrue(success['info'] == 'So far no errors found' or
                            success['info'] == 'So far no restricted library/function used')


if __name__ == '__main__':
    unittest.main()