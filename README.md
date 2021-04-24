# DeepChainMap
![PyPI](https://img.shields.io/pypi/v/deep-chainmap)
[![codecov](https://codecov.io/gh/neutrinoceros/deep_chainmap/branch/main/graph/badge.svg)](https://codecov.io/gh/neutrinoceros/deep_chainmap)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/neutrinoceros/deep_chainmap/main.svg)](https://results.pre-commit.ci/latest/github/neutrinoceros/deep_chainmap/main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A recursive subclass of the builtin Python class `collections.ChainMap`.

## Installation

```shell
pip install deep-chainmap
```

## Usage

The canonical use case for the builtin class `collections.ChainMap` is to
aggregate configuration data from layered mapping (basically dictionaries)
sources. However, it is not suited for non-flat (nested) mappings, the lookup
mechanism only works for the top level of a mapping.

`deep_chainmap.DeepChainMap` provides a simple solution to this problem by making
recurive lookups in arbitrarily deeply nested mappings. Let's illustrate this
with a simple example. We will simulate 3 layers of mapping, and pretend they
were obtained from different sources (a default configuration, a configuration
file and parameters configured at runtime).

```python
from deep_chainmap import DeepChainMap

default_layer = {
    "architecture": "gpu",
    "logging_level": "warning",
    "solver": "RK4",
    "database": {
        "url": "unset",
        "keep_in_sync": False,
    },
    "mesh": {
        "type": "rectangular",
        "resolution": {
            "x": {
                "npoints": 100,
                "spacing": "linear",
            },
            "y": {
                "npoints": 100,
                "spacing": "linear",
            },
            "z": {
                "npoints": 100,
                "spacing": "linear",
            },
        },
    },
}

config_file_layer = {
    "architecture": "cpu",
    "mesh": {
        "resolution": {
            "x": {
                "spacing": "log",
            },
            "z": {
                "npoints": 1,
            },
        },
    },
}

runtime_layer = {
    "logging_level": "debug",
    "database": {
        "url": "https://my.database.api",
        "keep_in_sync": True
    },
}

# now building a DeepChainMap
cm = DeepChainMap(runtime_layer, config_file_layer, default_layer)
```

Now when a single parameter is requested, it is looked up in each layer until a
value is found, by order of insertion. Here the `runtime_layer` takes priority
over the `config_file_layer`, which in turns takes priority over the
`default_layer`.
```python
>>> cm["logging_level"]
'debug'
>>> cm["mesh"]["resolution"]["x"]["spacing"]
'log'
>>> cm["mesh"]["resolution"]["x"]["npoints"]
100
```

A native `dict` view of a `DeepChainMap` object can be constructed via the `to_dict` method
```python
>>> cm.to_dict()
{
    'architecture': 'cpu',
    'logging_level': 'debug',
    'solver': 'RK4',
    'database': {
        'url': 'https://my.database.api',
        'keep_in_sync': True
    },
    'mesh': {
        'type': 'rectangular',
        'resolution': {
            'x': {'npoints': 100, 'spacing': 'log'},
            'y': {'npoints': 100, 'spacing': 'linear'},
            'z': {'npoints': 1, 'spacing': 'linear'}
        }
    }
}
```

Additionally, each submapping from any level can be retrieved as a new layered-mapping
```python
>>> cm["mesh"]
DeepChainMap({'resolution': {'x': {'spacing': 'log'}, 'z': {'npoints': 1}}},
             {'resolution': {'x': {'npoints': 100, 'spacing': 'linear'},
                             'y': {'npoints': 100, 'spacing': 'linear'},
                             'z': {'npoints': 100, 'spacing': 'linear'}},
              'type': 'rectangular'})
```

Which implies that they can be view as builtin dictionnaries as well
```python
>>> cm["mesh"].to_dict()
{
    'type': 'rectangular',
    'resolution': {
        'x': {'npoints': 100, 'spacing': 'log'},
        'y': {'npoints': 100, 'spacing': 'linear'},
        'z': {'npoints': 1, 'spacing': 'linear'}
    }
}
```
