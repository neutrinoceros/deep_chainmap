from collections import ChainMap
from collections.abc import Mapping

__version__ = "0.0.3"


class DeepChainMap(ChainMap):
    """A recursive subclass of ChainMap"""

    def __getitem__(self, key):
        submaps = [mapping for mapping in self.maps if key in mapping]
        if not submaps:
            return self.__missing__(key)
        if isinstance(submaps[0][key], Mapping):
            return DeepChainMap(*(submap[key] for submap in submaps))
        return super().__getitem__(key)

    def to_dict(self) -> dict:
        def depth_first_update(target: dict, source: Mapping) -> None:
            for key, val in source.items():
                if isinstance(val, Mapping):
                    if key not in target:
                        target[key] = {}
                    depth_first_update(target[key], val)
                else:
                    target[key] = val

        d = {}
        for mapping in reversed(self.maps):
            depth_first_update(d, mapping)

        return d
