[![Python Version](https://img.shields.io/pypi/pyversions/imio.svg)](https://pypi.org/project/imio)
[![PyPI](https://img.shields.io/pypi/v/imio.svg)](https://pypi.org/project/imio)
[![Downloads](https://pepy.tech/badge/imio)](https://pepy.tech/project/imio)
[![Wheel](https://img.shields.io/pypi/wheel/imio.svg)](https://pypi.org/project/imio)
[![Development Status](https://img.shields.io/pypi/status/imio.svg)](https://github.com/brainglobe/imio)
[![Tests](https://img.shields.io/github/workflow/status/brainglobe/imio/tests)](
    https://github.com/brainglobe/imio/actions)
[![Coverage Status](https://coveralls.io/repos/github/brainglobe/imio/badge.svg?branch=master)](https://coveralls.io/github/brainglobe/imio?branch=master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg)](https://github.com/brainglobe/imio)


# imio
Loading and saving of image data.

### About
The aim of imio is to be a lightweight image loading library for the file types
 supported by [cellfinder](https://github.com/brainglobe/cellfinder), and
 [brainreg](https://github.com/brainglobe/brainreg).

#### Supports loading of:
* Tiff stack `+`
* Tiff series (from a directory, a text file or a list of file paths). `*+`
* nrrd
* nifti (`.nii` & `.nii.gz`)

`*` Supports loading in parallel for speed

`+` Suports scaling on loading. E.g. downsampling to load images bigger than the 
available RAM

#### Supports saving of:
* Tiff stack
* Tiff series
* nifti 

### To install
```bash
pip install imio
```
