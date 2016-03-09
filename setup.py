"""Setup script for mtg_ssm."""

import sys

import setuptools


if sys.version_info < (3, 3):
    raise Exception('Python version < 3.3 are not supported.')


# Get version information without importing the package
__version__ = None
exec(open('mtg_ssm/version.py', 'r').read())  # pylint: disable=exec-used

SHORT_DESCRIPTION = (
    'A tool to manage Magic: the Gathering collection spreadsheets.')
LONG_DESCRIPTION = open('README.rst', 'r').read()

DEPENDENCIES = [l.strip() for l in open('requirements.txt', 'r')]

if sys.version_info < (3, 5):
    DEPENDENCIES.append('typing>=3.5.0.1')
if sys.version_info < (3, 4):
    DEPENDENCIES.append('enum34>=1.1.2')

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
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
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Topic :: Games/Entertainment',
]

setuptools.setup(
    name='mtg_ssm',
    version=__version__,
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='George Leslie-Waksman',
    author_email='waksman@gwax.com',
    url='https://github.com/gwax/mtg_ssm',
    packages=setuptools.find_packages(exclude=('tests*',)),
    license='MIT',
    platforms=['any'],
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
