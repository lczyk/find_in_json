# find_in_json

![GitHub Tag](https://img.shields.io/github/v/tag/lczyk/find_in_json?label=version)
[![Single file](https://img.shields.io/badge/single%20file%20-%20purple)](https://raw.githubusercontent.com/lczyk/find_in_json/main/src/find_in_json/find_in_json.py)
[![test](https://github.com/lczyk/find_in_json/actions/workflows/test.yml/badge.svg)](https://github.com/lczyk/find_in_json/actions/workflows/test.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
![Python versions](https://img.shields.io/badge/python-3.9%20~%203.13-blue)

Single-file Library for Finding Elements in JSON.

Find all instances in a JSON object (dict or list) matching the given key and/or value.
Returns a list of "paths" to the matching elements, where each path is a dot-separated
string of keys and indices. If no matches are found, returns an empty list. If no key
and no value is specified, returns the list of all paths in the JSON object.

Closely related to [compare_json](https://github.com/lczyk/compare_json) module.

Tested in Python 3.9+.

# Usage

```python
from find_in_json import find_in_json

json = {
    "apple": {
        "banana": [
            {
                "long": true,
                "color" [255, 255, 255]
            },
            {
                "long": false,
                "color": [128, 128, 128],
            }
        ]
    },
}

results = find_in_json(json, key="long")
assert results[0] == "apple.banana.[0].long"
assert results[0] == "apple.banana.[1].long"
```

## Install

Just copy the single-module file to your project and import it.

```bash
cp ./src/find_in_json/find_in_json.py tests/_find_in_json.py
```

Or even better, without checking out the repository:

```bash
curl https://raw.githubusercontent.com/lczyk/find_in_json/main/src/find_in_json/find_in_json.py > tests/_find_in_json.py
```

Note that like this *you take stewardship of the code* and you are responsible for keeping it up-to-date. If you change it that's fine (keep the license pls). That's the point here. You can also copy the code to your project and modify it as you wish.

If you want you can also build and install it as a package, but then the source lives somewhere else. That might be what you want though. 🤷‍♀️

```bash
pip install flit
flit build
ls dist/*
pip install dist/*.whl
```
