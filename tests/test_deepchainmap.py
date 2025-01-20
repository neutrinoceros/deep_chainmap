import pytest

from deep_chainmap import DeepChainMap

c1 = {
    "a": {
        "b": 2,
        "c": {
            "d": 4,
            "e": 5,
            "g": 77,
        },
    }
}
c2 = {"a": {}}

c3 = {"a": {"c": {"e": 6, "f": 66}}}

rcm = DeepChainMap(c3, c2, c1)


def test_empty():
    with pytest.raises(KeyError):
        DeepChainMap()["key"]


def test_get1():
    assert rcm["a"]["c"]["d"] == 4


def test_get2():
    assert rcm["a"]["c"]["e"] == 6


def test_dict1():
    assert rcm.to_dict() == {"a": {"b": 2, "c": {"d": 4, "e": 6, "f": 66, "g": 77}}}


def test_dict2():
    assert rcm["a"]["c"].to_dict() == {"d": 4, "e": 6, "f": 66, "g": 77}
