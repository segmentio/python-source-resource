from dateutil.parser import parse as parse_date
from segment_source import client as source
from dateutil.tz import tzlocal
from pydash import get, omit
import datetime
import numbers

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

    raise TypeError(("serialize_boolean() argument must be a boolean, string,",
        "or number, not a {}").format(type(val)))

class Resource:

    _parser_map = {
        'string': str,
        'float': float,
        'integer': int,
        'boolean': serialize_boolean,
        'datetime': serialize_datetime
    }

    def __init__(self, name, collection, fetch, schema, parent=None, transform=None):
        assert callable(fetch)
        assert callable(transform) or transform is None
        assert isinstance(parent, str) or parent is None

        self.name = name
        self.collection = collection
        self.parent = parent

        self._fetch = fetch
        self._schema = schema
        self._transform = transform

    def fetch(self, seed, consume):
        return self._fetch(seed, consume)

    def transform(self, obj, seed=None):
        ret = {}

        if self._transform:
            obj = self._transform(obj, seed)

        for column, definition in self._schema.items():
            source_name = definition.get('path', column)
            if isinstance(source_name, str):
                source_value = obj.get(source_name)
            elif isinstance(source_name, list):
                source_value = get(obj, source_name)
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
                ret[column] = parser_func(source_value)
            except (ValueError, TypeError) as err:
                message = "Failed to cast {} with value {} to {}".format(
                    column,
                    source_value,
                    definition['type'],
                )
                raise ValueError(message) from err

        return ret

    def set(self, obj):
        source.set(self.collection, obj['id'], omit(obj, 'id'))
