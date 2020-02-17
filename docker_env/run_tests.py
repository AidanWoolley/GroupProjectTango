import os
import yaml

import json
from subprocess import run

from Linter import Linter
from Validation import Validator

# Run validator and fail early on error
with open("out/validation_result.json", "w") as v_json:
    validation_result_str = Validator.validate("config.yaml")
    v_json.write(validation_result_str)
    validation_result = json.loads(validation_result_str)
    if len(validation_result["runners"][0]["errors"]) or len(validation_result["runners"][0]["failures"]):
        exit(1)

# Run quality check
with open("config.yaml") as conf_yaml:
    with open("out/quality_result.json", "w") as q_json:
        q_json.write(Linter.lint(yaml.safe_load(conf_yaml)["files"][0]))

# Run evaluator
run(["Rscript", "tester.R"])