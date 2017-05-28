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
TEST_DEPENDENCIES = [l.strip() for l in open('test_requirements.txt', 'r')]
SETUP_DEPENDENCIES = []
if {'pytest', 'test', 'ptr'}.intersection(sys.argv):
    SETUP_DEPENDENCIES.append('pytest-runner')

if sys.version_info < (3, 5):
    DEPENDENCIES.append('typing>=3.5.2,<4.0.0')
if sys.version_info < (3, 4):
    DEPENDENCIES.append('enum34>=1.1.6,<2.0.0')

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
    'Programming Language :: Python :: 3.6',
    'Topic :: Games/Entertainment',
]

EXTRAS = {
    'lxml': 'lxml>=3.7.2',
}

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
    setup_requires=SETUP_DEPENDENCIES,
    tests_require=TEST_DEPENDENCIES,
    extras_require=EXTRAS,
    entry_points={
        'console_scripts': [
            'mtg-ssm = mtg_ssm.ssm:main',
        ],
    },
)
