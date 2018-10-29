"""Marshmallow schemas for Scryfall api data."""

from typing import Dict

from marshmallow import fields
from marshmallow_annotations import registry
from marshmallow_annotations.ext.namedtuple import NamedTupleSchema
from marshmallow_enum import EnumField
from marshmallow_oneofschema import OneOfSchema

from mtg_ssm.scryfall import models


registry.register_field_for_type(models.URI, fields.URL)


@registry.field_factory(dict)
@registry.field_factory(Dict)
def dict_converter(converter, subtypes, opts):
    sub_opts = opts.pop('_interior', ({}, {}))
    return fields.Dict(
        keys=converter.convert(subtypes[0], sub_opts[0]),
        values=converter.convert(subtypes[1], sub_opts[1]),
        **opts
    )


@registry.field_factory(models.ScryfallColor)
def scryfall_color_converter(_converter, _subtypes, opts):
    return EnumField(models.ScryfallColor, by_value=True, **opts)


@registry.field_factory(models.ScryfallSetType)
def scryfall_settype_converter(_converter, _subtypes, opts):
    return EnumField(models.ScryfallSetType, by_value=True, **opts)


class BaseSchema(NamedTupleSchema):
    class Meta:
        dump_default_fields = False
        register_as_scheme = True
        strict = True

        class Fields:
            id_ = {'load_from': 'id', 'dump_to': 'id'}
            set_ = {'load_from': 'set', 'dump_to': 'set'}
            type_ = {'load_from': 'type', 'dump_to': 'type'}


class ScryfallListSchema(BaseSchema):
    class Meta:
        target = models.ScryfallList

    data = fields.Nested('ScryfallUberSchema', required=True, many=True)


class ScryfallBulkDataSchema(BaseSchema):
    class Meta:
        target = models.ScryfallBulkData


class ScryfallRelatedCardSchema(BaseSchema):
    class Meta:
        target = models.ScryfallRelatedCard


class ScryfallCardFaceSchema(BaseSchema):
    class Meta:
        target = models.ScryfallCardFace


class ScryfallCardSchema(BaseSchema):
    class Meta:
        target = models.ScryfallCard


class ScryfallSetSchema(BaseSchema):
    class Meta:
        target = models.ScryfallSet


class ScryfallUberSchema(OneOfSchema):
    type_field = 'object'
    type_schemas = {
        'bulk_data': ScryfallBulkDataSchema(),
        'related_card': ScryfallRelatedCardSchema(),
        'card_face': ScryfallCardFaceSchema(),
        'card': ScryfallCardSchema(),
        'set': ScryfallSetSchema(),
        'list': ScryfallListSchema(),
    }

    def get_obj_type(self, obj):
        class_and_label = [
            (models.ScryfallBulkData, 'bulk_data'),
            (models.ScryfallCard, 'card'),
            (models.ScryfallCardFace, 'card_face'),
            (models.ScryfallRelatedCard, 'related_card'),
            (models.ScryfallSet, 'set'),
            (models.ScryfallList, 'list'),
        ]
        for klass, label in class_and_label:
            print(klass, label, type(obj))
            if isinstance(obj, klass):
                return label
        raise Exception(f'Unknown object type {obj.__class__.__name__}')
