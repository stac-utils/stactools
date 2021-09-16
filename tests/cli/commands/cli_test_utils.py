import os
import json


def expected_json(filename):
    path = os.path.join(os.path.dirname(__file__), "expected", filename)
    with open(path) as f:
        return json.load(f)
