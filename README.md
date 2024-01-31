# brainglobe-utils

Shared general purpose tools for the BrainGlobe project, including [citation generation](#citations-for-brainglobe-tools).

## Installation

```bash
pip install brainglobe-utils
```

To also include the dependencies required for `napari`, use:

```bash
pip install brainglobe-utils[napari]
```

For development, clone this repository and install the dependencies with one of the following commands:

```bash
pip install -e .[dev]
pip install -e .[dev,napari]
```

## Citations for BrainGlobe tools

`brainglobe-utils` comes with the `cite-brainglobe` command line tool, to write citations for BrainGlobe tools for you so you don't need to worry about fetching the data yourself.
You can read about [how to use the tool](https://brainglobe.info/documentation/brainglobe-utils/citation-module.html) on the documentation website.
