"""
Single-file Library for Finding Elements in JSON.

Find all instances in a JSON object (dict or list) matching the given key and/or value.
Returns a list of "paths" to the matching elements, where each path is a dot-separated
string of keys and indices. If no matches are found, returns an empty list. If no key
and no value is specified, returns the list of all paths in the JSON object.
"""

# spell-checker: words tracebackhide Marcin Konowalczyk lczyk

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from typing_extensions import TypeAlias
else:
    TypeAlias = str  # type: ignore[assignment]


__version__ = "0.3.0"

__author__ = "Marcin Konowalczyk"

__all__ = [
    "ANY",
    "Path",
    "find_in_json",
    "get_by_path",
    "path_to_str",
    "set_by_path",
    "str_to_path",
]
__changelog__ = [
    ("0.3.0", "removed Any import and changed ANY_VALUE to ANY", "@lczyk"),
    ("0.2.0", "added get and set + changed path to list[str|int]", "@lczyk"),
    ("0.1.0", "initial version", "@lczyk"),
]

_missing = object()
_any = object()
ANY = _any

Path: TypeAlias = "list[str | int]"


def find_in_json(
    json: object,
    *,
    key: str | int | None = None,
    value: object = _any,
) -> list[Path]:
    """Find all instances in a JSON object (dict or list) matching the given key and/or value.
    Returns a list of "paths" to the matching elements, where each path is a list of keys and/or
    indices. If no matches are found, returns an empty list. If no key
    and no value is specified, returns the list of all paths in the JSON object."""
    key = None if key is ANY else key  # should not happen, but let's not break
    if key is None and value is _any:
        matcher = lambda k, v: True  # noqa: E731
    elif key is None and value is not _any:
        matcher = lambda k, v: v == value  # noqa: E731
    elif key is not None and value is _any:
        matcher = lambda k, v: k == key  # noqa: E731
    else:
        matcher = lambda k, v: k == key and v == value  # noqa: E731

    return _find_in_json(json, matcher, None, None)


def path_to_str(path: Path) -> str:
    """Convert a path (list of keys and indices) to a dot-separated string representation."""
    parts: list[str] = [f"[{p}]" if isinstance(p, int) else str(p) for p in path]
    return ".".join(parts)


def str_to_path(path: str) -> Path:
    """Convert a dot-separated string representation of a path to a list of keys and indices."""
    parts = path.split(".")
    result: Path = []
    for part in parts:
        if part.startswith("[") and part.endswith("]"):
            index_str = part[1:-1]
            result.append(int(index_str))
        else:
            result.append(part)
    return result


def get_by_path(
    data: object,
    path: Path,
    *,
    default: object = _missing,
    wrap_index: bool = True,
    raise_error: bool = True,
) -> object:
    """Get the value from a JSON object (dict or list) by the given path.
    If the path is invalid, returns an error message
    and a missing value object. If the path is valid, returns an empty error message and the value.
    If wrap is True, negative indices and indices greater than the length of the list are wrapped around."""
    msg, value = _get_by_path(data, path, wrap_index)
    if msg:
        if default is not _missing:
            return default
        elif raise_error:
            raise KeyError(msg)
        else:
            # NOTE: this is a bit hairy, since None is a valid value, but i guess if someone
            #       does not set the default and sets raise_error to False, they know what they are doing
            return None
    return value


def set_by_path(
    data: object,
    path: Path,
    value: object,
    *,
    wrap_index: bool = True,
    raise_error: bool = True,
) -> bool:
    """Set the value in a JSON object (dict or list) by the given path.
    If the path is invalid, returns an error message. If the path is valid, sets the value and returns True.
    """

    msg = _set_by_path(data, path, value, wrap_index)
    if msg and raise_error:
        raise KeyError(msg)
    return msg == ""


### Internal ###########################################################################################################


_Stack: TypeAlias = "list[str | int]"
_Matcher: TypeAlias = Callable[["str | int", object], bool]


def _find_in_json(
    json: object,
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


def _wrap_index(index: int, N: int) -> int:
    # wrap around once
    if index < 0:
        index += N
    elif index >= N:
        index -= N
    return index


def _get_by_path(json: object, path: Path, wrap: bool = True) -> tuple[str, object]:
    current = json
    for part in path:
        if isinstance(current, dict):
            if not isinstance(part, str):
                return f"Invalid path. Expected string key for dict, got {part!r}", _missing
            value = current.get(part, _missing)
            if value is _missing:
                return f"Key not found: {part!r}", _missing
            current = value
        elif isinstance(current, list):
            if not isinstance(part, int):
                return f"Invalid path. Expected integer index for list, got {part!r}", _missing
            index = _wrap_index(part, len(current)) if wrap else part
            if index < 0 or index >= len(current):
                return f"Index out of range: {index}", _missing
            current = current[index]
        else:
            return f"Invalid path. Expected dict or list, got {current!r}", _missing
    return "", current


def _set_by_path(json: object, path: Path, value: object, wrap: bool = True) -> str:
    current = json
    for i, part in enumerate(path):
        if i == len(path) - 1:
            # last part, set the value
            if isinstance(current, dict):
                if not isinstance(part, str):
                    return f"Invalid path. Expected string key for dict, got {part!r}"
                current[part] = value
                return ""
            elif isinstance(current, list):
                if not isinstance(part, int):
                    return f"Invalid path. Expected integer index for list, got {part!r}"
                index = _wrap_index(part, len(current)) if wrap else part
                if index < 0 or index >= len(current):
                    return f"Index out of range: {index}"
                current[index] = value
                return ""
            else:
                return f"Invalid path. Expected dict or list, got {current!r}"
        # traverse the path
        elif isinstance(current, dict):
            if not isinstance(part, str):
                return f"Invalid path. Expected string key for dict, got {part!r}"
            if part not in current or not isinstance(current[part], (dict, list)):
                # create a new dict if the key does not exist or is not a dict/list
                current[part] = {}
            current = current[part]
        elif isinstance(current, list):
            if not isinstance(part, int):
                return f"Invalid path. Expected integer index for list, got {part!r}"
            index = _wrap_index(part, len(current)) if wrap else part
            if index < 0 or index >= len(current):
                return f"Index out of range: {index}"
            if not isinstance(current[index], (dict, list)):
                # create a new dict if the element is not a dict/list
                current[index] = {}
            current = current[index]
        else:
            return f"Invalid path. Expected dict or list, got {current!r}"
    return ""


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
