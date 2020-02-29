import sys

from json import dump as json_dump
from os.path import abspath
from subprocess import run as sp_run

from tango import Linter
from tango import Validator

if __name__ == '__main__':
    config_yaml_path = abspath(sys.argv[1])

    v_res = Validator.validate(config_yaml_path)
    with open("/home/tango/out/validation.json", "w") as v_file:
        json_dump(v_res, v_file)

    if v_res["runners"][0]["errors"] or v_res["runners"][0]["failures"]:
        # Code is syntactically incorrect or using forbidden libs/funcs
        # Exit early
        exit(-1)

    l_res = Linter.lint(config_yaml_path)
    with open("/home/tango/out/quality.json", "w") as q_file:
        json_dump(l_res, q_file)

    # Actual test evaluation is handled entirely in R
    sp_run(["Rscript", "/home/tango/tester.R"], timeout=60)
