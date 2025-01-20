from collections import ChainMap
from collections.abc import Mapping
from typing import Any

__version__ = "0.1.2"


def _depth_first_update(target: dict[Any, Any], source: Mapping[Any, Any]) -> None:
    for key, val in source.items():
        if not isinstance(val, Mapping):
            target[key] = val
            continue

        if key not in target:
            target[key] = {}
        _depth_first_update(target[key], val)


class DeepChainMap(ChainMap[Any, Any]):
    """A recursive subclass of ChainMap"""

    def __getitem__(self, key: Any) -> Any:
        submaps = [mapping for mapping in self.maps if key in mapping]
        if not submaps:
            return self.__missing__(key)
        if isinstance(submaps[0][key], Mapping):
            return DeepChainMap(*(submap[key] for submap in submaps))
        return super().__getitem__(key)

    def to_dict(self) -> dict[Any, Any]:
        d: dict[Any, Any] = {}
        for mapping in reversed(self.maps):
            _depth_first_update(d, mapping)
        return d
