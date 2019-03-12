"""Marshmallow schemas for Scryfall api data."""

import collections
from decimal import Decimal
from enum import EnumMeta
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Type
from typing import Union

import marshmallow
from marshmallow import fields
from marshmallow_annotations import AnnotationSchema
from marshmallow_annotations import BaseConverter
from marshmallow_annotations import registry
from marshmallow_enum import EnumField
from marshmallow_oneofschema import OneOfSchema

from mtg_ssm.scryfall import models
from mtg_ssm.scryfall.third_party import marshmallow_fields

registry.register_field_for_type(models.URI, fields.URL)


@registry.field_factory(Decimal)
def decimal_converter(
    _converter: BaseConverter, _subtypes: Any, opts: Dict[str, Any]
) -> fields.Field:
    """Decimal field factory that always sets as_string."""
    return fields.Decimal(as_string=True, **opts)


@registry.field_factory(dict)
@registry.field_factory(Dict)
def dict_converter(
    converter: BaseConverter, subtypes: Any, opts: Dict[str, Any]
) -> fields.Field:
    """Dictionary field factory for marshmallow annotations."""
    sub_opts = opts.pop("_interior", ({}, {}))
    return marshmallow_fields.Dict(
        keys=converter.convert(subtypes[0], sub_opts[0]),
        values=converter.convert(subtypes[1], sub_opts[1]),
        **opts,
    )


class TupleField(fields.List):
    """Tuple field based on tuple() wrapping List field."""

    def _serialize(self, value: Any, attr: Any, obj: Any) -> Optional[Tuple[Any, ...]]:
        ret = super()._serialize(value, attr, obj)
        if ret is None:
            return None
        return tuple(ret)

    def _deserialize(
        self, value: Any, attr: Any, data: Any
    ) -> Optional[Tuple[Any, ...]]:
        ret = super()._deserialize(value, attr, data)
        if ret is None:
            return None
        return tuple(ret)


@registry.field_factory(Sequence)
@registry.field_factory(collections.abc.Sequence)
def sequence_converter(
    converter: BaseConverter, subtypes: Any, opts: Dict[str, Any]
) -> fields.Field:
    """Sequence field factory that treats sequences as lists."""
    sub_opts = opts.pop("_interior", {})
    return TupleField(converter.convert(subtypes[0], sub_opts), **opts)


def _register_enum(enum_class: EnumMeta) -> None:
    """Enum field registration helper function."""

    @registry.field_factory(enum_class)
    def _enum_converter(
        _converter: BaseConverter, _subtypes: Any, opts: Dict[str, Any]
    ) -> fields.Field:
        return EnumField(enum_class, by_value=True, **opts)


STR_ENUMS: Sequence[EnumMeta] = (
    models.ScryBorderColor,
    models.ScryCardFrame,
    models.ScryCardLayout,
    models.ScryRarity,
    models.ScryColor,
    models.ScryFormat,
    models.ScryFrameEffect,
    models.ScryGame,
    models.ScryLegality,
    models.ScrySetType,
)
for _str_enum in STR_ENUMS:
    _register_enum(_str_enum)


class BaseSchema(AnnotationSchema):
    """Shared marshmallow schema helper class."""

    object = fields.String(dump_only=True)

    @marshmallow.validates_schema(pass_original=True)
    def disallow_unknown_fields(
        self, _: Any, original_data: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> None:
        """Check that no extra fields have been passed in."""
        if isinstance(original_data, (list, tuple)):
            unknowns = [sorted(set(o) - set(self.fields)) for o in original_data]
            if any(unknowns):
                raise marshmallow.ValidationError(
                    f"{type(self).__name__} Unknown fields: {repr(unknowns)}"
                )
        else:
            unknown = sorted(set(original_data) - set(self.fields))
            if unknown:
                raise marshmallow.ValidationError(
                    f"{type(self).__name__} Unknown fields: {repr(unknown)}"
                )

    @marshmallow.post_load
    def make_target(self, data: Dict[str, Any]) -> Any:
        """Post load, deserialize to target class."""
        return self.opts.target(**data)

    @marshmallow.post_dump
    def remove_none(  # pylint: disable=no-self-use
        self, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Post dump, strip null values."""
        return {k: v for k, v in data.items() if v is not None}


@registry.field_factory(models.ScryObject)
def _scryfall_converter(
    _converter: BaseConverter, _subtypes: Any, opts: Dict[str, Any]
) -> fields.Field:
    """Treat ScryfallObject references as OneOfSchema lookups."""
    return fields.Nested("ScryfallUberSchema", **opts)


MODELS: Sequence[Type[models.ScryObject]] = (
    models.ScryRelatedCard,
    models.ScryCardFace,
    models.ScryCard,
    models.ScrySet,
    models.ScryBulkData,
    models.ScryObjectList,
)
OBJECT_SCHEMAS: Dict[str, BaseSchema] = {}
for _model in MODELS:
    _meta = type(
        "Meta", (), {"target": _model, "register_as_scheme": True, "strict": True}
    )
    _schema_class = type(f"{_model.__name__}Schema", (BaseSchema,), {"Meta": _meta})
    globals()[_schema_class.__name__] = _schema_class
    OBJECT_SCHEMAS[_model.object] = _schema_class()


class ScryfallUberSchema(OneOfSchema):
    """Lookup master schema for ScryfallObject subclasses."""

    class Meta:  # TODO: do we need this?
        """Marshmallow configuration options."""

        strict = True

    type_field = "object"
    type_schemas = OBJECT_SCHEMAS

    def get_obj_type(self, obj: models.ScryObject) -> str:
        return getattr(obj, self.type_field)
