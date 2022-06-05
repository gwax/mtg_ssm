mtg-ssm - Magic: the Gathering Spreadsheet Manager
===================================================

.. image:: https://img.shields.io/coveralls/gwax/mtg_ssm.svg
    :target: https://coveralls.io/r/gwax/mtg_ssm

.. image:: https://img.shields.io/travis/gwax/mtg_ssm/master.svg
    :target: https://travis-ci.org/gwax/mtg_ssm

.. image:: https://img.shields.io/pypi/v/mtg-ssm.svg
    :target: https://pypi.python.org/pypi/mtg-ssm/

.. image:: https://img.shields.io/pypi/pyversions/mtg-ssm.svg
    :target: https://pypi.python.org/pypi/mtg-ssm/

.. image:: https://img.shields.io/pypi/dm/mtg-ssm.svg
    :target: https://pypi.python.org/pypi/mtg-ssm/

`mtg-ssm`_ is a tool for creating/updating user-friendly spreadsheets with
Magic: the Gathering collection information. The tool can also
import/export data to/from these spreadsheets to other formats, such as
CSV files.

.. _mtg-ssm: https://github.com/gwax/mtg_ssm

As a matter of convenience, you can store the created spreadsheet in
Dropbox, Google Drive, or the like and access your collection from
anywhere.

Installation
============

mtg-ssm is available on PyPI so, if you have python (>=3.6) and pip
installed on your system, you should be able to get mtg-ssm by entering
the following into a terminal:

.. code:: bash

    pip3 install mtg_ssm

Updates can be performed by entering:

.. code:: bash

    pip3 install -U mtg_ssm

You can verify installation from the terminal by running:

.. code:: bash

    mtg-ssm --help

Usage
=====

For first time use, you will want to create an empty spreadsheet with
card data:

.. code:: bash

    mtg-ssm create collection.xlsx

In the future, when new sets are released, you will want to update your
collection spreadsheet while keeping existing counts:

.. code:: bash

    mtg-ssm update collection.xlsx

Existing collections
--------------------

If you already have your cards in another collection store, you might
want to import that collection into your card spreadsheet.

First create an input csv file:

.. code:: bash

    mtg-ssm create input_data.csv

Then modify the template to match your counts and import into your
spreadsheet:

.. code:: bash

    mtg-ssm merge collection.xlsx input_data.csv

Troubleshooting
===============

Windows 7 and up
----------------

Certain unicode characters (such as U+2605 ★) may not be mapped
correctly on Windows systems, causing errors when mtg-ssm tries
to map data from Scryfall.  This can occur in Command Prompt,
Powershell, or other terminal emulators that rely on the system
region settings (Such as MSYS2 MinGW).  The below steps should
help to resolve this issue.

-   Open up Control panel.
-   Go to Clock and Region.
-   Click Region.
-   Go to the Administrative tab (second tab)
-   Click Change System Locale.
-   Check "Beta: Use Unicode UTF-8 for worldwide language support".
-   Restart your computer.

Contributions
=============

Pull requests are welcome and contributions are greatly appreciated.

Issues can be reported via GitHub.

Acknowledgments
===============

-   `Wizards of the Coast`_: For making Magic: the Gathering and continuing
    to support it. Off and on, it's been my favorite hobby since the
    early '90s.
-   `Scryfall`_: Scryfall is a fantastic resource for anyone trying to lookup
    cards or build software on top of up to date Magic card information.
-   `MTG JSON`_: MTG JSON is an amazing resource for anyone looking to build
    tools around magic card data. Before Scryfall, MTG JSON was my primary
    source for card data and, without it, mtg-ssm would not exist.

.. _Wizards of the Coast: http://magic.wizards.com
.. _Scryfall: https://scryfall.com
.. _MTG JSON: http://mtgjson.com


Changelog
=========

Development
-----------

-   ...

2.2.0
-----

-   Build and release using GitHub Actions
-   Switch over to pydantic for Scryfall data deserialization
-   Bug fixes for newer sets that do not include a numeric component to ther
    collector numbers.

2.1.3
-----

-   Update models to match scryfall as of 2020-09-09
-   Cache failures on model change fixes

2.1.1
-----

-   Fix Scryfall data fetching on Windows.
-   Update models to match scryfall as of 2020-02-08

2.1.0
-----

-   Add support for filtering card data by set type

    -   For example, `mtg_ssm --set-types token,emblem create tokens.xlsx` to
        create a spreadsheet for tracking tokens and emblems.

2.0.1
-----

-   Updated models to match scryfall as of 2019-09-10

2.0.0
-----

-   Switched from mtgjson to Scryfall as a data source
-   Broke existing spreadsheets

    -   ``update`` will rebuild / upgrade existing sheets

    -   rebuild lookup doesn't work very well for basic lands, double check
        your counts

    -   rebuild lookup may result in double counting for Flip / split / DFC
        cards, double-check your counts

    -   a number of cards count not reliably be remapped and will raise
        exceptions; if you have any copies of these cards, you will need
        to remove them from your existing spreadsheet and re-add them
        after the update

    -   promo cards are particularly hard hit as Scryfall and MTGJSON model
        promo sets very differently.

-   Dropped deckbox serializer
-   Removed support for Python 3.4, 3.5

1.3.6
-----

-   Removed support for Python 3.3
-   Test and bug fixes
-   Handle newer versions of mtgjson

1.3.5
-----

-   Remove profiling code. If we care, we can invoke profiling with:

    .. code:: sh

        python -m cProfile -o mtg_ssm.prof mtg_ssm/ssm.py create collection.xlsx

-   Fix wheel generation to only build py3 wheels.

1.3.4
-----

-   Increase in verbosity when looking up cards by heuristics (instead of id).

1.3.3
-----

-   Fixed support for Ae/Æ
-   Increased verbosity when searching for cards with a mismatched id
-   Performance improvements
-   Add tests to catch potential missing card issues

1.3.2
-----

-   Changed the backup file naming convention; date is now before extension
-   Minor tweaks and performance enhancements

1.3.1
-----

-   Fix bug where were were never actually reading set names from xlsx
    files.

1.3.0
-----

-   Complete rework of cli (see `--help` for details)

    -   cli is **NOT** the same; old commands will **NOT** work
    -   new global argument flags and dialect selection mechanisms
    -   create: create a new collection
    -   update: update an existing collection
    -   merge: merge multiple collections
    -   diff: get a diff of two collections

-   Lots of under the hood changes and performance improvements
-   Files are still compatible

1.2.4
-----

-   Remove workarounds introduced in 1.2.3

1.2.3
-----

-   Hack to work around missing "releaseDate" and "type" in MTG JSON 3.3.14

1.2.2
-----

-   Add "All Cards" page with index of all cards in XlsxSerializer.

1.2.1
-----

-   Add support for deckbox.org import/export.
-   Backend improvements.

1.2.0
-----

-   Complete rework of the serialization architecture.
-   Rebuild of the manager cli.
-   Incompatible CLI interface changes. See help for new usage information.

1.1.0
-----

-   Complete rework of the data model storage. Drop sqlite based data models in
    favor of custom classes and dict based indexes.
-   Switch to accepting all versions of MTGJSON instead of bumping for every
    release.

1.0.2
-----

-   Version bump MTGJSON support.

1.0.1
-----

-   Fixed some PyPI related issues.

1.0.0
-----

-   Initial stable release.
