import sys
from setuptools import find_namespace_packages, setup
import codecs
import os.path

# edit author dictionary as necessary
author_dict = {
    "Joseph D. Hughes": "jdhughes@usgs.gov",
    "Martijn Russcher": "Martijn.Russcher@deltares.nl",
    "Christian D. Langevin": "langevin@usgs.gov",
    "Julian Hofer": "Julian.Hofer@deltares.nl",
}
__author__ = ", ".join(author_dict.keys())
__author_email__ = ", ".join(s for _, s in author_dict.items())


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


long_description = read("README.md")


setup(
    name="modflowapi",
    description="modflowapi is an extension to the xmipy Python package.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=__author__,
    author_email=__author_email__,
    url="https://github.com/MODFLOW-USGS/modflowapi.git",
    license="CC0",
    platforms="Windows, Mac OS-X, Linux",
    install_requires=[
        "xmipy",
    ],
    python_requires=">=3.6",
    packages=find_namespace_packages(exclude=("etc",)),
    version=get_version("modflowapi/__init__.py"),
    classifiers=["Topic :: Scientific/Engineering :: Hydrology"],
)
