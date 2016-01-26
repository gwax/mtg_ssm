# mtg_ssm - Magic: the Gathering Collection Database

[![Build Status](https://travis-ci.org/gwax/mtg_ssm.svg?branch=master)](https://travis-ci.org/gwax/mtg_ssm)

This is a tool for creating/updating user-friendly spreadsheets with
Magic: the Gathering collection information. The tool can also import/export
data to/from these spreadsheets to other formats, such as CSV files.

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

You should now be able to run mtgss_manager from the root of the repository:

```bash
./mtgss_manager.py --help
```

# Usage

For first time use, you will want to create an empty spreadsheet with card data:

```bash
./mtgss_manager.py collection.xlsx create
```
In the future, when new sets are released, you can update your spreadsheet
with new cards:

```bash
./mtgss_manager.py collection.xlsx update
```

## Existing collections

If you already have your cards in another collection store, you might want to
import that collection into your card database.

First create an example csv file:

```bash
./mtgss_manager.py collection.xlsx create
./mtgss_manager.py collection.xlsx export collection.csv.example
```

Then create a matching csv and import into your database:

```bash
./mtgss_manager.py collection.xlsx import collection.csv
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
