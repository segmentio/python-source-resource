import datetime
import numbers
import logging
import typing

from dateutil.parser import parse as parse_date
from dateutil.tz import tzlocal
from pydash import get


def parse_datetime(timestamp: typing.Union[datetime.datetime, str]) -> str:
    if isinstance(timestamp, datetime.datetime):
        value = timestamp
    else:
        value = parse_date(timestamp)

    with_timezone = value.replace(tzinfo=value.tzinfo or tzlocal())
    return with_timezone.isoformat()


def parse_boolean(val: typing.Union[bool, str, typing.SupportsInt]) -> bool:
    if isinstance(val, bool):
        return val

    if isinstance(val, str):
        lowercased = val.lower()
        if lowercased == 'false':
            return False
        if lowercased == 'true':
            return True

    if isinstance(val, numbers.Number):
        as_int = int(val)
        if as_int == 0:
            return False
        if as_int == 1:
            return True

    raise TypeError("serialize_boolean() argument must be a boolean, string, "
                    "or number, not a {}".format(type(val)))


class RawObj(object):
    def __init__(self, data: dict, collection: str, schema: dict) -> None:
        self.data = data
        self.collection = collection
        self.schema = schema


class Obj(object):
    def __init__(self, id: str, properties: dict, collection: str) -> None:
        self.id = str(id) # Comment(@Ilya): cast integer ids to string, per Marketo IDs
        self.properties = properties
        self.collection = collection


class Resource(object):
    parent = None  # type: typing.Optional[Resource]

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def collection(self) -> str:
        raise NotImplementedError

    @property
    def schema(self) -> dict:
        raise NotImplementedError

    def fetch(self, seed: typing.Any) -> typing.Generator[typing.Union[dict, RawObj, Obj], None, None]:
        """
        can yield values of:
        dict (in this case the're casted to instances RawObj using resource's default collection and schema)
        object of RawObj (such objects will be transformed to Obj using resource's transform method)
        object of Obj (will be set as is)
        """
        raise NotImplementedError

    _parser_map = {
        'string': str,
        'float': float,
        'integer': int,
        'boolean': parse_boolean,
        'datetime': parse_datetime
    }

    def get_subresource_fetch_arg(self, raw_obj: RawObj, resource: "Resource") -> typing.Any:
        """
        Returns a value that will be used as a "seed" argument to enqueue child resource fetch tasks.
        If None is returned, child resource tasks won't be enqueued.
        """
        return raw_obj

    def transform(self, raw_obj: RawObj, seed: typing.Any = None) -> Obj:
        obj_id = None
        obj_properties = {}

        for column, definition in raw_obj.schema.items():
            source_name = definition.get('path', column)
            if isinstance(source_name, str):
                source_value = raw_obj.data.get(source_name)
            elif isinstance(source_name, list):
                source_value = get(raw_obj.data, source_name)
            else:
                raise ValueError("Invalid path: {}".format(source_name))

            if source_value is None: continue

            if callable(definition['type']):
                parser_func = definition['type']
            elif definition['type'] in self._parser_map:
                parser_func = self._parser_map[definition['type']]
            else:
                raise ValueError("Invalid type: {}".format(definition['type']))

            try:
                if column == 'id':
                    obj_id = parser_func(source_value)
                else:
                    obj_properties[column] = parser_func(source_value)

            except (ValueError, TypeError) as err:
                message = "Failed to cast {} with value {} to {}".format(
                    column,
                    source_value,
                    definition['type'],
                )
                raise ValueError(message) from err

        if not obj_id:
            logging.warning("raw object without id: collection=%s properties=%s", raw_obj.collection, raw_obj.data)

        return Obj(
            id=obj_id,
            properties=obj_properties,
            collection=raw_obj.collection,
        )
