"""Setup script for mtg_ssm."""

import sys

import setuptools

if sys.version_info < (3, 6):
    raise Exception("Python version < 3.6 are not supported.")

# Get version information without importing the package
__version__ = None
exec(open("mtg_ssm/version.py", "r").read())  # pylint: disable=exec-used

SHORT_DESCRIPTION = "A tool to manage Magic: the Gathering collection spreadsheets."
LONG_DESCRIPTION = open("README.rst", "r").read()

DEPENDENCIES = [l.strip() for l in open("requirements.txt", "r")]
TEST_DEPENDENCIES = [l.strip() for l in open("test_requirements.txt", "r")]
if sys.version_info < (3, 7):
    DEPENDENCIES.append("dataclasses")

CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Operating System :: MacOS",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: OS Independent",
    "Operating System :: POSIX",
    "Operating System :: Unix",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Topic :: Games/Entertainment",
]

EXTRAS = {"lxml": "lxml>=3.7.2"}

setuptools.setup(
    name="mtg_ssm",
    version=__version__,
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author="George Leslie-Waksman",
    author_email="waksman@gwax.com",
    url="https://github.com/gwax/mtg_ssm",
    packages=setuptools.find_packages(exclude=("tests*",)),
    package_data={"mtg_ssm": ["py.typed"]},
    license="MIT",
    platforms=["any"],
    keywords="mtg magic collection tracking spreadsheet",
    classifiers=CLASSIFIERS,
    install_requires=DEPENDENCIES,
    tests_require=TEST_DEPENDENCIES,
    extras_require=EXTRAS,
    entry_points={"console_scripts": ["mtg-ssm = mtg_ssm.ssm:main"]},
)
