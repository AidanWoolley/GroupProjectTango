from json import load as load_json
from subprocess import run as sp_run
from flask import Flask, url_for, request, render_template
from pretty_msgs import from_validation, from_quality

app = Flask(__name__)


@app.route('/')
def index():
    with open("./edukate_demo.html") as f:
        return f.read()


@app.route('/test', methods=["POST"])
def test_code():
    with open("/tango/src/demo.R", "w") as r_code:
        r_code.write(request.form["code"])
    with open("/tango/testcases/demo.R", "w") as r_test:
        r_test.write(request.form["tests"])
    sp_run([
        "docker", "run", "--rm",
        "--mount", "type=bind,src=/tmp/tango/src,dst=/home/tango/src,readonly=true",
        "--mount", "type=bind,src=/tmp/tango/testcases,dst=/home/tango/testcases,readonly=true",
        "--mount", "type=bind,src=/tmp/tango/out,dst=/home/tango/out",
        "awoolley10/tango-demo"
    ])
    with open("/tango/out/validation.json") as v_json:
        validation_result = from_validation(load_json(v_json)["runners"][0])
    if len(validation_result["successes"]) == 3:
        with open("/tango/out/quality.json") as q_json:
            q_res = load_json(q_json)["runners"][0]
        q_e = from_quality(q_res["errors"])  # Quality errors
        q_score = round(100 * q_res["score"])

        with open("/tango/out/evaluation.json") as e_json:
            e_res = load_json(e_json)["runners"][0]
        try:
            e_s = e_res["successes"]
        except KeyError:
            e_s = []
        try:
            e_f = e_res["failures"]
        except KeyError:
            e_f = []
        try:
            e_e = e_res["errors"]
        except KeyError:
            e_e = []
    else:
        q_e = None
        q_score = None
        e_s = None
        e_f = None
        e_e = None

    return render_template(
        "feedback.j2",
        v_s=validation_result["successes"],
        v_f=validation_result["failures"],
        v_e=validation_result["errors"],
        q_score=q_score,
        q_e=q_e,
        e_s=e_s,
        e_f=e_f,
        e_e=e_e
    )


with app.test_request_context():
    url_for("static", filename='demo.css')
    url_for("static", filename='codemirror.css')
    url_for("static", filename='ayu-dark.css')
    url_for("static", filename='codemirror.js')
    url_for("static", filename='r.js')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
