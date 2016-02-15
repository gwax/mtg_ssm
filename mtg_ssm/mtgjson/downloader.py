"""Download required remote files."""

import codecs
import collections
import json
import os
import zipfile

import requests


MTGJSON_ADDRESS = 'http://mtgjson.com/json/'
VERSION_FILENAME = 'version-full.json'
ALLSETS_FILENAME = 'AllSets.json.zip'


class DownloadError(Exception):
    """Raised if the downloader fails to fetch a file."""


class VersionError(Exception):
    """Raised if the remote version is newer than the max supported version."""


def fetch_mtgjson(data_folder):
    """Check version and fetch (if needed) mtgjson file to data_folder."""
    version_filename = os.path.join(data_folder, VERSION_FILENAME)
    if os.path.exists(version_filename):
        with open(version_filename, 'r') as version_file:
            local_version_data = json.load(version_file)
            local_version = tuple(
                int(v) for v in local_version_data['version'].split('.'))
    else:
        local_version = (0, 0, 0)

    ver_req = requests.get(MTGJSON_ADDRESS + VERSION_FILENAME)
    if ver_req.status_code != 200:
        raise DownloadError(
            'Could not fetch version: {}'.format(ver_req.reason))
    remote_version_data = ver_req.json()
    remote_version = tuple(
        int(v) for v in remote_version_data['version'].split('.'))

    if local_version >= remote_version:
        return False

    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    allsets_filename = os.path.join(data_folder, ALLSETS_FILENAME)
    mtg_req = requests.get(MTGJSON_ADDRESS + ALLSETS_FILENAME)
    with open(allsets_filename, 'wb') as allsets_file:
        allsets_file.write(mtg_req.content)
    with open(version_filename, 'wb') as version_file:
        version_file.write(ver_req.content)
    return True


def read_mtgjson(data_folder):
    """Read data from mtgjson file and return loaded contents."""
    allsets_filename = os.path.join(data_folder, ALLSETS_FILENAME)
    with zipfile.ZipFile(allsets_filename, 'r') as allsets_zipfile:
        [datafilename] = allsets_zipfile.namelist()
        datafile = allsets_zipfile.open(datafilename)
        reader = codecs.getreader('utf-8')
        mtgdata = json.load(
            reader(datafile), object_pairs_hook=collections.OrderedDict)
    return mtgdata
