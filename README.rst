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

This is a tool for creating/updating user-friendly spreadsheets with
Magic: the Gathering collection information. The tool can also
import/export data to/from these spreadsheets to other formats, such as
CSV files.

As a matter of convenience, you can store the created spreadsheet in
Dropbox, Google Drive, or the like and access your collection from
anywhere.

Installation
============

mtg-ssm is available on PyPI so, if you have python (>=3.3) and pip
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

    mtg-ssm collection.xlsx

In the future, when new sets are released, running the same command will
update your collection spreadsheet while keeping existing counts:

.. code:: bash

    mtg-ssm collection.xlsx

Existing collections
--------------------

If you already have your cards in another collection store, you might
want to import that collection into your card spreadsheet.

First create an example csv file:

.. code:: bash

    mtg-ssm --format csv collection.csv.example

Then modify the template to match your counts and import into your
spreadsheet:

.. code:: bash

    mtg-ssm collection.xlsx collection.csv

In development
==============

This tool is a work in progress. It is fully working now and I use it
for tracking my own, personal collection, but it is somewhat tailored to
my needs. There are, also, quite a few features that I would like to add
and bits of code to cleanup (of course, every project always needs some
code cleanup).

Contributions
=============

Pull requests are welcome and contributions are greatly appreciated.

Acknowledgments
===============

-  `Wizards of the Coast`_: For making Magic: the Gathering and continuing
   to support it. Off and on, it's been my favorite hobby since the
   early '90s.
-  `MTG JSON`_: MTG JSON is an amazing resource for anyone looking to build
   tools around magic card data. It is pretty much **THE** source for
   structured magic card data. Without MTG JSON this project would not have
   been possible.

.. _Wizards of the Coast: http://magic.wizards.com
.. _MTG JSON: http://mtgjson.com
