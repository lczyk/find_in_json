from find_in_json import ANY, get_by_path, path_to_str, set_by_path, str_to_path
from find_in_json import find_in_json as _find_in_json


def find_in_json(json: object, key: object = ANY, value: object = ANY) -> list[str]:
    return [path_to_str(path) for path in _find_in_json(json, key=key, value=value)]  # type: ignore


def test_find_in_json() -> None:
    json_data = {"a": {"b": {"c": "value1", "d": "value2"}, "e": "value3"}, "f": [{"g": "value4"}, {"h": "value5"}]}

    matches = find_in_json(json_data, key="c")
    assert len(matches) == 1
    assert matches[0] == "a.b.c"

    matches = find_in_json(json_data, value="value5")
    assert len(matches) == 1
    assert matches[0] == "f.[1].h"

    matches = find_in_json(json_data, key="g", value="value4")
    assert len(matches) == 1
    assert matches[0] == "f.[0].g"

    matches = find_in_json(json_data, key="nonexistent")
    assert len(matches) == 0


def test_find_in_json_multiple() -> None:
    json_data = {
        "a": {"b": {"c": "value"}, "d": {"c": "value"}},
        "e": [{"c": "value"}, {"f": "value"}],
    }

    matches = find_in_json(json_data, key="c", value="value")
    assert len(matches) == 3
    assert set(matches) == {"a.b.c", "a.d.c", "e.[0].c"}


def test_find_in_json_no_key_no_value() -> None:
    json_data = {"a": {"b": "value"}, "c": ["value", {"d": "value"}]}
    matches = find_in_json(json_data)
    assert set(matches) == {
        "a",
        "a.b",
        "c",
        "c.[0]",
        "c.[1]",
        "c.[1].d",
    }


def test_find_in_json_numeric_key() -> None:
    json_data = {"a": {"1": "value1", "2": "value2"}, "b": [{"3": "value3"}, {"4": "value4"}]}
    matches = find_in_json(json_data, key=1)
    assert len(matches) == 1
    assert matches[0] == "b.[1]"
    assert get_by_path(json_data, str_to_path("b.[1]")) == {"4": "value4"}


def test_get_and_set_by_path() -> None:
    json_data = {"a": {"b": {"c": "value1", "d": "value2"}, "e": "value3"}, "f": [{"g": "value4"}, {"h": "value5"}]}

    value = get_by_path(json_data, str_to_path("a.b.c"))
    assert value == "value1"

    value = get_by_path(json_data, str_to_path("f.[1].h"))
    assert value == "value5"

    value = get_by_path(json_data, str_to_path("nonexistent.path"), default="default_value")
    assert value == "default_value"

    value = get_by_path(json_data, str_to_path("nonexistent.path"), raise_error=False)
    assert value is None

    success = set_by_path(json_data, str_to_path("a.b.c"), "new_value1")
    assert success
    assert get_by_path(json_data, str_to_path("a.b.c")) == "new_value1"
