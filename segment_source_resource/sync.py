import typing

from gevent.pool import Pool
from gevent.thread import Greenlet

from segment_source_resource.exceptions import PublicError, RunError
from segment_source_resource.resource import RawObj, Obj, Resource
from segment_source import client as source


_errors = []


def _create_error_handler(collection: str) -> typing.Callable[[Greenlet], None]:
    def handler(thread: Greenlet) -> None:
        print("{} failed".format(collection))
        print(thread.exception)

        if isinstance(thread.exception, PublicError):
            message = str(thread.exception)
        else:
            message = 'Unexpected failure'
            _errors.append(thread.exception)

        source.report_error(message, collection)

    return handler


def _process_resource(resources: typing.List[Resource], seed: typing.Any, resource: Resource):
    threads = Pool(10)

    for raw_obj in resource.fetch(seed):
        if not isinstance(raw_obj, (Obj, RawObj)):
            raw_obj = RawObj(data=raw_obj, collection=resource.collection, schema=resource.schema)

        if isinstance(raw_obj, Obj):
            obj = raw_obj
        else:
            obj = resource.transform(raw_obj, seed)

        source.set(obj.collection, obj.id, obj.properties)
        thread = threads.spawn(_enqueue_children, resources, raw_obj, resource)
        thread.link_exception(_create_error_handler(resource.collection))

    threads.join()


def _enqueue_children(resources: typing.List[Resource], seed: typing.Any, parent: Resource):
    threads = Pool(10)

    for resource in [r for r in resources if r.parent == parent.name]:
        prepared_seed = parent.get_subresource_fetch_arg(seed, resource)
        if prepared_seed is None:
            continue

        thread = threads.spawn(_process_resource, resources, prepared_seed, resource)
        thread.link_exception(_create_error_handler(resource.collection))

    threads.join()


def execute(resources: typing.List[Resource], seed: typing.Any = None):
    threads = Pool(10)
    for resource in [r for r in resources if not r.parent]:
        thread = threads.spawn(_process_resource, resources, seed, resource)
        thread.link_exception(_create_error_handler(resource.collection))

    threads.join()

    if len(_errors):
        raise RunError("Resource group failed", _errors)
