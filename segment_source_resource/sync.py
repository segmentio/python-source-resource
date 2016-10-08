import sys

from gevent.pool import Group

from segment_source_resource.exceptions import PublicError, RunError
from segment_source_resource.resource import RawObj, Obj
from segment_source import client as source


_errors = []


def _create_error_handler(collection):
    def handler(thread):
        print("{} failed".format(collection))
        print(thread.exception)

        if isinstance(thread.exception, PublicError):
            message = thread.exception.__str__()
        else:
            message = 'Unexpected failure'
            _errors.append(thread.exception)

        source.report_error(message, collection)

    return handler


def _process_resource(resources, seed, resource):
    for raw_obj in resource.fetch(seed):
        if not isinstance(raw_obj, (Obj, RawObj)):
            raw_obj = RawObj(data=raw_obj, collection=resource.collection, schema=resource.schema)

        if isinstance(raw_obj, Obj):
            obj = raw_obj
        else:
            obj = resource.transform(raw_obj, seed)

        source.set(obj.collection, obj.id, obj.properties)
        _enqueue_children(resources, raw_obj, resource)


def _enqueue_children(resources, seed, parent):
    threads = Group()
    for resource in [r for r in resources if r.parent == parent.name]:
        thread = threads.spawn(_process_resource, resources, seed, resource)
        thread.link_exception(_create_error_handler(resource.collection))

    threads.join()


def execute(resources, seed=None):
    threads = Group()
    for resource in [r for r in resources if not r.parent]:
        thread = threads.spawn(_process_resource, resources, seed, resource)
        thread.link_exception(_create_error_handler(resource.collection))

    threads.join()

    if len(_errors):
        raise RunError("Resource group failed", _errors)
