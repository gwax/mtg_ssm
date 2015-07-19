# mtgcdb - Magic: the Gathering Collection Database

[![Build Status](https://travis-ci.org/gwax/mtgcdb.svg?branch=master)](https://travis-ci.org/gwax/mtgcdb)

This is a tool for creating/updating user-friendly Office Open XML (XLSX)
spreadsheets with Magic: the Gathering collection information. It can also
be used to create somewhat user-friendly CSV files with collection information.

As a matter of convenience, you can store the created spreadsheet in
Dropbox, Google Drive, or the like and access your collection from
any device.

## Note

This tool is something that I am developing in my spare time, primarily for
the purpose of tracking my own card collection so installation and ease of
use may be a little tricky if you don't have an understanding of git and python.

# Installation

As of right now, there is no simple means of installation.

You will need a working copy of python3 and pip3 on your system.

Clone this repository, and then from the root of the repository run:

```bash
pip3 install -r requirements.txt
```

You should now be able to run mtgcdb_manager from the root of the repository:

```bash
./mtgcdb_manager --help
```

# Usage

For first time use, you will want to start by updating your card database:

```bash
./mtgcdb_manager update_cards
```

Then you can create a new spreadsheet to store your collection:

```bash
./mtgcdb_manager write_xlsx collection.xlsx
```

In the future, when new sets are released, you can update your spreadsheet
with new cards:

```bash
./mtgcdb_manager update_xlsx collection.xlsx
```

## Existing collections

If you already have your cards in another collection store, you might want to
import that collection into your card database.

First create an example csv file:

```bash
./mtgcdb_manager write_csv collection.csv.example
```

Then create a matching csv and import into your database:

```bash
./mtgcdb_manager read_csv collection.csv
```

From here, you can write to xlsx (or csv) and set aside your csv import file:

```bash
./mtgcdb_manager write_xlsx collection.xlsx
rm collection.csv
```

# In development

This tool is a work in progress. It is fully working now and I use it for
tracking my own, personal collection, but it is somewhat tailored to my
needs. There are, also, quite a few features that I would like to add and
bits of code to cleanup (of course, every project always needs some code
cleanup).

# Contributions

Pull requests are welcome and contributions are greatly appreciated.

# Acknowledgments

* [Wizards of the Coast](http://magic.wizards.com/): For making Magic: the
Gathering and continuing to support it. Off and on, it's been my favorite
hobby since the early '90s.
* Robert at [MTG JSON](http://mtgjson.com): MTG JSON is an amazing resource
for anyone looking to build tools around magic card data. Without MTG JSON
this project would not have been possible.
