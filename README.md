# modflowapi

[![CI](https://github.com/MODFLOW-USGS/modflowapi/actions/workflows/ci.yml/badge.svg)](https://github.com/MODFLOW-USGS/modflowapi/actions/workflows/ci.yml)
[![GitHub contributors](https://img.shields.io/github/contributors/MODFLOW-USGS/modflowapi)](https://img.shields.io/github/contributors/MODFLOW-USGS/modflowapi)
[![GitHub tag](https://img.shields.io/github/tag/MODFLOW-USGS/modflowapi.svg)](https://github.com/MODFLOW-USGS/modflowapi/tags/latest)

[![PyPI License](https://img.shields.io/pypi/l/modflowapi)](https://pypi.python.org/pypi/modflowapi)
[![PyPI Status](https://img.shields.io/pypi/status/modflowapi.png)](https://pypi.python.org/pypi/modflowapi)
[![PyPI Format](https://img.shields.io/pypi/format/modflowapi)](https://pypi.python.org/pypi/modflowapi)
[![PyPI Version](https://img.shields.io/pypi/v/modflowapi.png)](https://pypi.python.org/pypi/modflowapi)
[![PyPI Versions](https://img.shields.io/pypi/pyversions/modflowapi.png)](https://pypi.python.org/pypi/modflowapi)

[![Anaconda License](https://anaconda.org/conda-forge/modflowapi/badges/license.svg)](https://anaconda.org/conda-forge/modflowapi/badges/license.svg)
[![Anaconda Version](https://anaconda.org/conda-forge/modflowapi/badges/version.svg)](https://anaconda.org/conda-forge/modflowapi)
[![Anaconda Updated](https://anaconda.org/conda-forge/modflowapi/badges/latest_release_date.svg)](https://anaconda.org/conda-forge/modflowapi)

An extension to [xmipy](https://pypi.org/project/xmipy/) for the MODFLOW API.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [Installation](#installation)
- [Documentation](#documentation)
- [Citation](#citation)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

The `modflowapi` Python package can be used to access functionality in the eXtended Model Interface (XMI) wrapper (XmiWrapper) 
and additional functionality specific to the MODFLOW API. Currently it is a joint development of the USGS and Deltares.

## Installation

`modflowapi` requires Python 3.8+, with:

```shell
numpy
pandas
xmipy
```

To install `modflowapi` with pip:

```
pip install modflowapi
```

Or with conda:

```
conda install -c conda-forge modflowapi
```

## Documentation

Examples using `modflowapi` and its extensions can be found in the [Quickstart](examples/notebooks/Quickstart.ipynb) and the [Extensions](examples/notebooks/MODFLOW-API_extensions_objects.ipynb) notebooks. An example of using the MODFLOW API to monitor heads during a simulation can be found in the [Head Monitor Example](examples/notebooks/Head_Monitor_Example.ipynb) Notebook. 

## Citation

Hughes, Joseph D., Russcher, M. J., Langevin, C. D., Morway, E. D. and McDonald, R. R., 2022, The MODFLOW Application Programming Interface for simulationcontrol and software interoperability: Environmental Modelling & Software, v. 148, p. 105257, [doi:10.1016/j.envsoft.2021.105257](https://doi.org/10.1016/j.envsoft.2021.105257).
