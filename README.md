[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Main](https://github.com/py-why/graphs/actions/workflows/main.yml/badge.svg)](https://github.com/py-why/graphs/actions/workflows/main.yml)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![codecov](https://codecov.io/gh/py-why/graphs/branch/main/graph/badge.svg?token=H1reh7Qwf4)](https://codecov.io/gh/py-why/graphs)

# graphs

Playground for PRable stuff into networkx. Do not use this repo unless you are working with the pywhy team on networkx-implementations.

Base classes for graphs that extend [networkx](https://github.com/networkx/networkx) to be used in other PyWhy libraries.

Please refer to the networkx code to see how things should be structured. The intention is to PR functionality in this repo directly by:

1. copy-pasting relevant files into networkx
2. find+replace "graphs" with "networkx" and
3. then submitting PR

# Documentation

See the [development version documentation](https://pywhy.github.io/graphs/dev/index.html).

# Installation

Installation is best done via `pip` installing directly from the github API.

    pip install -U https://github.com/pywhy/graphs/archive/main.zip

## Dependencies

Minimally, graphs requires:

    * Python (>=3.8)
    * NumPy
    * SciPy
    * Networkx

## User Installation

To install the package from github, clone the repository and then `cd` into the directory:

    pip install -e .
