"""Extensionts to marshmallow 2.x pulled from 3.x

https://github.com/marshmallow-code/marshmallow/blob/b1ddf571679d9f45aa265c9f905398515412d4c1/marshmallow/fields.py

Copyright 2019 Steven Loria and contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
# pylint: skip-file

import collections
import datetime as dt
import decimal
import numbers
import uuid
import warnings

from marshmallow import class_registry, utils, validate
from marshmallow.base import FieldABC, SchemaABC
from marshmallow.compat import basestring, text_type
from marshmallow.exceptions import ValidationError
from marshmallow.fields import Field
from marshmallow.utils import missing as missing_
from marshmallow.validate import Validator


class Dict(Field):
    """A dict field. Supports dicts and dict-like objects. Optionally composed
    with another `Field` class or instance.
    Example: ::
        numbers = fields.Dict(values=fields.Float(), keys=fields.Str())
    :param Field values: A field class or instance for dict values.
    :param Field keys: A field class or instance for dict keys.
    :param kwargs: The same keyword arguments that :class:`Field` receives.
    .. note::
        When the structure of nested data is not known, you may omit the
        `values` and `keys` arguments to prevent content validation.
    .. versionadded:: 2.1.0
    """

    default_error_messages = {"invalid": "Not a valid mapping type."}

    def __init__(self, values=None, keys=None, **kwargs):
        super(Dict, self).__init__(**kwargs)
        if values is None:
            self.value_container = None
        elif isinstance(values, type):
            if not issubclass(values, FieldABC):
                raise ValueError(
                    '"values" must be a subclass of ' "marshmallow.base.FieldABC"
                )
            self.value_container = values()
        else:
            if not isinstance(values, FieldABC):
                raise ValueError(
                    '"values" must be of type ' "marshmallow.base.FieldABC"
                )
            self.value_container = values
        if keys is None:
            self.key_container = None
        elif isinstance(keys, type):
            if not issubclass(keys, FieldABC):
                raise ValueError(
                    '"keys" must be a subclass of ' "marshmallow.base.FieldABC"
                )
            self.key_container = keys()
        else:
            if not isinstance(keys, FieldABC):
                raise ValueError('"keys" must be of type ' "marshmallow.base.FieldABC")
            self.key_container = keys

    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        if not self.value_container and not self.key_container:
            return value
        if isinstance(value, collections.Mapping):
            values = value.values()
            if self.value_container:
                values = [
                    self.value_container._serialize(item, attr, obj) for item in values
                ]
            keys = value.keys()
            if self.key_container:
                keys = [self.key_container._serialize(key, attr, obj) for key in keys]
            return dict(zip(keys, values))
        self.fail("invalid")

    def _deserialize(self, value, attr, data):
        if not isinstance(value, collections.Mapping):
            self.fail("invalid")
        if not self.value_container and not self.key_container:
            return value

        errors = {}
        values = list(value.values())
        keys = list(value.keys())
        if self.key_container:
            for idx, key in enumerate(keys):
                try:
                    keys[idx] = self.key_container.deserialize(key)
                except ValidationError as e:
                    errors[key] = [
                        "Invalid key: {}".format(message) for message in e.messages
                    ]
        if self.value_container:
            for idx, item in enumerate(values):
                try:
                    values[idx] = self.value_container.deserialize(item)
                except ValidationError as e:
                    values[idx] = e.data
                    key = keys[idx]
                    if key not in errors:
                        errors[key] = []
                    errors[key].extend(
                        ["Invalid value: {}".format(message) for message in e.messages]
                    )
        result = dict(zip(keys, values))

        if errors:
            raise ValidationError(errors, data=result)

        return result
