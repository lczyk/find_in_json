"""
Single-file Library for Finding Elements in JSON.

Find all instances in a JSON object (dict or list) matching the given key and/or value.
Returns a list of "paths" to the matching elements, where each path is a dot-separated
string of keys and indices. If no matches are found, returns an empty list. If no key
and no value is specified, returns the list of all paths in the JSON object.
"""

# spell-checker: words tracebackhide Marcin Konowalczyk lczyk

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from typing_extensions import TypeAlias
else:
    TypeAlias = str  # type: ignore[assignment]


__version__ = "0.1.0"

__author__ = "Marcin Konowalczyk"


__changelog__ = [
    ("0.1.0", "initial version", "@lczyk"),
]

_any = object()
ANY_VALUE = _any


def find_in_json(json: object, *, key: str | int | None = None, value: Any = _any) -> list[str]:
    """Find all instances in a JSON object (dict or list) matching the given key and/or value.
    Returns a list of "paths" to the matching elements, where each path is a dot-separated
    string of keys and indices. If no matches are found, returns an empty list. If no key
    and no value is specified, returns the list of all paths in the JSON object."""

    matches = _find_in_json(json, _make_matcher(key, value), None, None)
    _matches = [[f"[{s}]" if isinstance(s, int) else s for s in m] for m in matches]
    return [".".join(m) for m in _matches]


### Internal ###########################################################################################################


_Stack: TypeAlias = "list[str | int]"
_Matcher: TypeAlias = Callable[["str | int", Any], bool]


def _make_matcher(key: str | int | None, value: Any) -> _Matcher:
    if key is None and value is _any:
        return lambda k, v: True
    elif key is None and value is not _any:
        return lambda k, v: v == value
    elif key is not None and value is _any:
        return lambda k, v: k == key
    else:
        return lambda k, v: k == key and v == value


def _find_in_json(
    json: Any,
    matcher_fun: _Matcher,
    _matches: list[_Stack] | None,
    _stack: _Stack | None,
) -> list[_Stack]:
    matches: list[_Stack] = _matches if _matches is not None else []
    stack: _Stack = _stack if _stack is not None else []

    if isinstance(json, dict):
        for k, v in json.items():
            stack = [*stack, k] if stack else [k]
            if matcher_fun(k, v):
                matches.append(stack.copy())
            _find_in_json(v, matcher_fun, matches, stack)
            stack.pop()

    elif isinstance(json, list):
        for key, v in enumerate(json):
            stack = [*stack, key] if stack else [key]
            if matcher_fun(key, v):
                matches.append(stack.copy())
            _find_in_json(v, matcher_fun, matches, stack)
            stack.pop()
    else:
        pass

    return matches


__license__ = """
Copyright 2025 Marcin Konowalczyk

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

1.  Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

2.  Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.

3.  Neither the name of the copyright holder nor the names of its
    contributors may be used to endorse or promote products derived from
    this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
