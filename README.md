[![Python Version](https://img.shields.io/pypi/pyversions/imio.svg)](https://pypi.org/project/imio)
[![PyPI](https://img.shields.io/pypi/v/imio.svg)](https://pypi.org/project/imio)
[![Downloads](https://pepy.tech/badge/imio)](https://pepy.tech/project/imio)
[![Wheel](https://img.shields.io/pypi/wheel/imio.svg)](https://pypi.org/project/imio)
[![Development Status](https://img.shields.io/pypi/status/imio.svg)](https://github.com/brainglobe/imio)
[![Tests](https://img.shields.io/github/workflow/status/brainglobe/imio/tests)](
    https://github.com/brainglobe/imio/actions)
[![codecov](https://codecov.io/gh/brainglobe/imio/branch/master/graph/badge.svg?token=M1BXRDJ9V4)](https://codecov.io/gh/brainglobe/imio)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
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

## Contributing
Contributions to imio are more than welcome. Please see the [contributing guide](https://github.com/brainglobe/.github/blob/main/CONTRIBUTING.md).

## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/jaimergp"><img src="https://avatars.githubusercontent.com/u/2559438?v=4?s=100" width="100px;" alt="jaimergp"/><br /><sub><b>jaimergp</b></sub></a><br /><a href="https://github.com/brainglobe/imio/commits?author=jaimergp" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/crousseau"><img src="https://avatars.githubusercontent.com/u/13150960?v=4?s=100" width="100px;" alt="Charly Rousseau"/><br /><sub><b>Charly Rousseau</b></sub></a><br /><a href="https://github.com/brainglobe/imio/commits?author=crousseau" title="Code">💻</a> <a href="#ideas-crousseau" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/brainglobe/imio/commits?author=crousseau" title="Tests">⚠️</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
