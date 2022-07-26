from os import path

from setuptools import find_packages, setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

requirements = [
    "numpy",
    "scikit-image",
    "tifffile",
    "pynrrd",
    "nibabel",
    "tqdm",
    "natsort",
    "psutil",
    "slurmio >= 0.0.5",
    "imlib",
    "nibabel >= 2.1.0",
]

setup(
    name="imio",
    version="0.2.4-rc0",
    description="Loading and saving of image data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black",
            "pytest-cov",
            "pytest",
            "coverage",
            "bump2version",
            "pre-commit",
            "flake8",
        ]
    },
    python_requires=">=3.7",
    packages=find_packages(exclude=("tests", "tests.*")),
    include_package_data=True,
    url="https://github.com/brainglobe/imio",
    author="Charly Rousseau, Adam Tyson",
    author_email="code@adamltyson.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
    ],
    zip_safe=False,
)
