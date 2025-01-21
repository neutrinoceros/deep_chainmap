# DeepChainMap
[![PyPI](https://img.shields.io/pypi/v/deep-chainmap?logo=pypi&logoColor=white&label=PyPI)](https://pypi.org/project/deep-chainmap/)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/neutrinoceros/deep_chainmap/main.svg)](https://results.pre-commit.ci/latest/github/neutrinoceros/deep_chainmap/main)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

A recursive subclass of [`collections.ChainMap`](https://docs.python.org/3/library/collections.html#collections.ChainMap).

## Installation

```shell
python -m pip install deep-chainmap
```

## Usage

The canonical use case for `collections.ChainMap` is to aggregate configuration
data from layered mapping (basically dictionaries) sources. However, it is not
suited for non-flat (nested) mappings, since the lookup mechanism only works for
the top level of a mapping.

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

Note that submappings at any level can be retrieved as new
`DeepChainMap` instances
```python
>>> cm["mesh"]
DeepChainMap({'resolution': {'x': {'spacing': 'log'}, 'z': {'npoints': 1}}},
             {'resolution': {'x': {'npoints': 100, 'spacing': 'linear'},
                             'y': {'npoints': 100, 'spacing': 'linear'},
                             'z': {'npoints': 100, 'spacing': 'linear'}},
              'type': 'rectangular'})
```

The other important feature is the `to_dict` method, which constructs a builtin
`dict` from a `DeepChainMap`

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
An important implication is that the `DeepChainMap` class enables a very simple,
functional implementation of a depth-first dict-merge algorithm as

```python
from deep_chainmap import DeepChainMap

def depth_first_merge(*mappings) -> dict:
    return DeepChainMap(*mappings).to_dict()
```



## Limitations

As the standard `collections.ChainMap` class, `DeepChainMap` does not, by
design, perform any kind of data validation. Rather, it is _assumed_ that the
input mappings are similar in structure, meaning that a key which maps to a dict
in one of the input mappings is assumed to map to dict instances as well in
every other input mapping. Use the excellent
[schema](https://pypi.org/project/schema/) library or similar projects for this
task.

:warning: An important difference with `collections.ChainMap` is that, when
setting a (key, value) pair in a `DeepChainMap` instance, the new value is
stored in the first mapping _which already contains the parent map_. For example
if we run
```python
>>> cm["mesh"]["resolution"]["x"]["spacing"] = "exp"
```
The affected layer is `config_file_layer` rather than `runtime_layer`, as one
can see
```python
>>> config_file_layer
{
    'architecture': 'cpu',
    'mesh': {
        'resolution': {
            'x': {'spacing': 'exp'},
            'z': {'npoints': 1}
        }
    }
}
>>> runtime_layer
{
    'logging_level': 'debug',
    'database': {
        'url': 'https://my.database.api',
        'keep_in_sync': True
    }
}
```
This behaviour is a side effect on an implementation detail and subject to
change in a future version. Please do not rely on it.
