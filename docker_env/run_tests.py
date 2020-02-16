import os
import subprocess as sp
from Linter import Linter


file_to_lint = os.listdir("src")[0]
with open("out/quality_result.json", "w") as q_json:
    q_json.write(Linter.lint(os.path.join("./src/", file_to_lint)))
sp.run(["Rscript", "tester.R"])