import json
import os

FILE_PATH = "cases.json"

def save_case(data, user):
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, "w") as f:
            json.dump([], f)

    with open(FILE_PATH, "r") as f:
        cases = json.load(f)

    cases.append({
        "user": user,
        **data
    })

    with open(FILE_PATH, "w") as f:
        json.dump(cases, f, indent=2)