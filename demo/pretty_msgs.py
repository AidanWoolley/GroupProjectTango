val_types = {
    "restricted library": "Restricted library usage",
    "restricted function": "Restricted function usage",
    "syntax": "Syntax check",
    "unknown library": "Unknown library",
    "unknown function": "Unknown function",
    "unknown variable": "Unknown variable"
}

def from_validation(val_res):
    for results in val_res["successes"]:
        results["type"] = val_types[results["type"]]

    for results in val_res["failures"]:
        results["type"] = val_types[results["type"]]

    for results in val_res["errors"]:
        results["type"] = val_types[results["type"]]

    return val_res


qual_types = {
    "info": "Style Issue",
    "warning": "Warning"
}


def from_quality(qual_res):
    for error in qual_res:
        error["type"] = qual_types[error["type"]]
    return qual_res