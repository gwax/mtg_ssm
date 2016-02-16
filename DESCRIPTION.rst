mtg\_ssm - Magic: the Gathering Spreadsheet Manager
===================================================

|Build Status| |Coverage Status|

This is a tool for creating/updating user-friendly spreadsheets with
Magic: the Gathering collection information. The tool can also
import/export data to/from these spreadsheets to other formats, such as
CSV files.

As a matter of convenience, you can store the created spreadsheet in
Dropbox, Google Drive, or the like and access your collection from
anywhere.

Installation
============

mtg\_ssm is available on PyPI so, if you have python (>=3.4) and pip
installed on your system, you should be able to get mtg\_ssm by entering
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

    mtg-ssm collection.xlsx create

In the future, when new sets are released, you can update your
spreadsheet with new cards:

.. code:: bash

    mtg-ssm collection.xlsx update

Existing collections
--------------------

If you already have your cards in another collection store, you might
want to import that collection into your card database.

First create an example csv file:

.. code:: bash

    mtg-ssm collection.xlsx create
    mtg-ssm collection.xlsx export collection.csv.example

Then create a matching csv and import into your database:

.. code:: bash

    mtg-ssm collection.xlsx import collection.csv

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

-  `Wizards of the Coast <http://magic.wizards.com/>`__: For making
   Magic: the Gathering and continuing to support it. Off and on, it's
   been my favorite hobby since the early '90s.
-  `MTG JSON <http://mtgjson.com>`__: MTG JSON is an amazing resource
   for anyone looking to build tools around magic card data. It is
   pretty much **THE** source for structured magic card data. Without
   MTG JSON this project would not have been possible.

.. |Build Status| image:: https://travis-ci.org/gwax/mtg_ssm.svg?branch=master
   :target: https://travis-ci.org/gwax/mtg_ssm
.. |Coverage Status| image:: https://coveralls.io/repos/github/gwax/mtg_ssm/badge.svg?branch=master
   :target: https://coveralls.io/github/gwax/mtg_ssm?branch=master
