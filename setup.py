"""Setup script for mtg_ssm."""

import sys

from setuptools import setup, find_packages


if sys.version_info < (3, 4):
    raise Exception('Python version < 3.4 are not supported.')


with open('requirements.txt', 'r') as reqfile:
    DEPENDENCIES = [l.strip() for l in reqfile]

with open('README.md', 'r') as descfile:
    LONG_DESCRIPTION = descfile.read()

# Get version information without importing the package
__version__ = None
with open('mtg_ssm/version.py', 'r') as verfile:
    exec(verfile.read())  # pylint: disable=exec-used

SHORT_DESCRIPTION = (
    'A tool to manage Magic: the Gathering collection spreadsheets.')

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: MIT License',
    'Operating System :: MacOS',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: OS Independent',
    'Operating System :: POSIX',
    'Operating System :: Unix',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Topic :: Games/Entertainment',
]

setup(
    name='mtg_ssm',
    version=__version__,
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='George Leslie-Waksman',
    author_email='waksman@gwax.com',
    url='https://github.com/gwax/mtg_ssm',
    packages=find_packages(exclude=['tests']),
    license='MIT',
    keywords='mtg magic collection tracking spreadsheet',
    classifiers=CLASSIFIERS,
    install_requires=DEPENDENCIES,
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'mtg-ssm = mtg_ssm.manager:main',
        ],
    },
)
