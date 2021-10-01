from setuptools import setup, find_packages

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
    version="0.0.1a",
    description="Loading and saving of image data.",
    install_requires=requirements,
    extras_require={"dev": ["black", "pytest-cov", "pytest", "coverage",]},
    python_requires=">=3.6",
    packages=find_packages(),
    include_package_data=True,
    url="https://github.com/adamltyson/imio",
    author="Adam Tyson",
    author_email="adam.tyson@ucl.ac.uk",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
    ],
    zip_safe=False,
)
