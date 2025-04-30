from collections import ChainMap
from collections.abc import Mapping
from typing import Generic, TypeVar

__version__ = "0.1.2"

K = TypeVar("K")
V = TypeVar("V")


def _depth_first_update(target: dict[K, V], source: Mapping[K, V]) -> None:
    for key, val in source.items():
        if not isinstance(val, Mapping):
            target[key] = val
            continue

        if key not in target:
            target[key] = {}
        _depth_first_update(target[key], val)


class DeepChainMap(Generic[K, V], ChainMap[K, V]):
    """A recursive subclass of ChainMap"""

    def __getitem__(self, key: K) -> V:
        submaps = [mapping for mapping in self.maps if key in mapping]
        if not submaps:
            return self.__missing__(key)
        if isinstance(submaps[0][key], Mapping):
            return DeepChainMap(*(submap[key] for submap in submaps))
        return super().__getitem__(key)

    def to_dict(self) -> dict[K, V]:
        d: dict[K, V] = {}
        for mapping in reversed(self.maps):
            _depth_first_update(d, mapping)
        return d
