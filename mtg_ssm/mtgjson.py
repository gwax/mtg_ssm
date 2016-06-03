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


class Error(Exception):
    """Base error class for this module."""


class DownloadError(Error):
    """Raised if the downloader fails to fetch a file."""


def fetch_mtgjson(data_path):
    """Check version and fetch (if needed) mtgjson file to data_path."""
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    elif not os.path.isdir(data_path):
        raise DownloadError('data_path: %s must be a folder' % data_path)

    version_filename = os.path.join(data_path, VERSION_FILENAME)
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

    print('Downloading mtgjson data.')
    allsets_filename = os.path.join(data_path, ALLSETS_FILENAME)
    mtg_req = requests.get(MTGJSON_ADDRESS + ALLSETS_FILENAME)
    with open(allsets_filename, 'wb') as allsets_file:
        allsets_file.write(mtg_req.content)
    with open(version_filename, 'wb') as version_file:
        version_file.write(ver_req.content)
    return True


def read_mtgjson(data_path):
    """Read data from mtgjson file and return loaded contents."""
    allsets_filename = os.path.join(data_path, ALLSETS_FILENAME)
    with zipfile.ZipFile(allsets_filename, 'r') as allsets_zipfile:
        [datafilename] = allsets_zipfile.namelist()
        datafile = allsets_zipfile.open(datafilename)
        reader = codecs.getreader('utf-8')
        mtgdata = json.load(
            reader(datafile), object_pairs_hook=collections.OrderedDict)
    # Hack to work around mtg_ssm/issues/1
    mtgdata['W16'].setdefault('releaseDate', '2016-04-08')
    mtgdata['W16'].setdefault('type', 'starter')
    return mtgdata
