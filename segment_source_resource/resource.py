import datetime
import numbers

from dateutil.parser import parse as parse_date
from dateutil.tz import tzlocal
from pydash import get


def serialize_datetime(timestamp):
    if isinstance(timestamp, datetime.date):
        date = timestamp
    else:
        date = parse_date(timestamp)

    with_timezone = date.replace(tzinfo=date.tzinfo or tzlocal())
    timestring = with_timezone.isoformat()

    return timestring


def serialize_boolean(val):
    if isinstance(val, bool): return val

    if isinstance(val, str):
        lowercased = val.lower()
        if lowercased == 'false': return False
        if lowercased == 'true': return True

    if isinstance(val, numbers.Number):
        as_int = int(val)
        if as_int == 0: return False
        if as_int == 1: return True

    raise TypeError("serialize_boolean() argument must be a boolean, string, "
                    "or number, not a {}".format(type(val)))


class RawObj(object):
    def __init__(self, data, collection, schema):
        self.data = data
        self.collection = collection
        self.schema = schema


class Obj(object):
    def __init__(self, id, properties, collection):
        self.id = id
        self.properties = properties
        self.collection = collection


class Resource(object):
    parent = None

    @property
    def name(self):
        raise NotImplementedError

    @property
    def collection(self):
        raise NotImplementedError

    @property
    def schema(self):
        raise NotImplementedError

    def fetch(self, seed):
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
        'boolean': serialize_boolean,
        'datetime': serialize_datetime
    }

    def transform(self, raw_obj, seed=None):
        obj = Obj(
            id=None,
            properties={},
            collection=raw_obj.collection,
        )

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
                    obj.id = parser_func(source_value)
                else:
                    obj.properties[column] = parser_func(source_value)

            except (ValueError, TypeError) as err:
                message = "Failed to cast {} with value {} to {}".format(
                    column,
                    source_value,
                    definition['type'],
                )
                raise ValueError(message) from err

        return obj
