from find_in_json import find_in_json

# from find_in_json import find_in_json, get_from_json


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
    # assert get_from_json(json_data, "b.[1]") == {"4": "value4"}
